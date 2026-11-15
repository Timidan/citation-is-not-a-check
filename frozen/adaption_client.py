"""Direct, resumable Adaption requests with one persistent credit ledger.

No automatic retries. Credentials never enter request artifacts.
"""
import hashlib
import json
import os
import re
from pathlib import Path
import sqlite3
import time
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING

API = 'https://api.prod.adaptionlabs.ai/api/v1'
RATES = {
    'qwen3.8-27b': (0.039, 0.0039, 1.25),
    'glm-5.3-flash': (0.15, 0.03, 0.50),
    'deepseek-v4-flash': (0.04444, 0.001414, 0.13332),
}
PACKAGE_ROOT = Path('/home/timidan/Documents/Codex/2026-11-13/https-apartresearch-com-sprints-ai-x/outputs/multi-model-followup')
EXECUTION_ROOT = PACKAGE_ROOT / 'execution'
_DISPATCH_LOCK = threading.Lock()
_LAST_DISPATCH = 0.0
_RATE_LIMIT_UNTIL = 0.0
DISPATCH_SPACING_SECONDS = 3.1


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(data)
    temporary.replace(path)


def key_from_file(path):
    key = ''
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if line.startswith('ADAPTION_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('\"\'')
    if not key:
        key = os.environ.get('ADAPTION_API_KEY', '')
    if not key or not key.startswith('pt_'):
        raise RuntimeError('Adaption API key is not configured.')
    return key


def models(key):
    request = urllib.request.Request(API + '/models?type=hosted',
                                     headers={'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def estimated_charge(model, input_tokens, output_tokens, cached=0):
    standard, cache, output = [Decimal(str(n)) for n in RATES[model]]
    cost = ((input_tokens-cached)*standard + cached*cache + output_tokens*output) / Decimal(1000000)
    return float(cost.quantize(Decimal('0.000001'), rounding=ROUND_CEILING))


def reservation(body):
    # Byte bound plus a generous message/template allowance, not a tokenizer.
    # Calibration must check actual provider usage against this bound.
    content = json.dumps({'input': body['input'], 'instructions': body['instructions']},
                         ensure_ascii=False)
    input_bound = len(content.encode()) + 1024
    upper = estimated_charge(body['model'], input_bound, body['max_output_tokens'])
    return input_bound, upper * 1.25


def initialize(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(root / 'ledger.sqlite', timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS requests '
                   '(id TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL, '
                   'state TEXT NOT NULL, reserved REAL NOT NULL, charged REAL, '
                   'model TEXT NOT NULL, started TEXT NOT NULL, finished TEXT, error TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY,value TEXT)')


def totals(root):
    with sqlite3.connect(Path(root) / 'ledger.sqlite', timeout=30) as db:
        rows = db.execute('SELECT state,COUNT(*),SUM(COALESCE(charged,reserved)) '
                          'FROM requests GROUP BY state').fetchall()
    return {'cap_credits': None, 'accounted_credits': sum(row[2] for row in rows),
            'states': {s: {'requests': n, 'credits': cost} for s,n,cost in rows}}


def transport_failure(record):
    return record.get('fatal', False) and (
        record.get('http_status') in (408, 500, 502, 503, 504)
        or (record.get('http_status') == 429 and record.get('rate_limit_wait_seconds') is not None)
        or record.get('error') in (
            'ConnectionResetError', 'ConnectionAbortedError', 'BrokenPipeError',
            'TimeoutError', 'URLError', 'RemoteDisconnected', 'IncompleteRead',
            'Stream ended without a terminal response or usage'))


def reconcile_startup(root,key):
    with sqlite3.connect(root/'ledger.sqlite',timeout=30) as db:
        rows=db.execute('SELECT id FROM requests WHERE state=?',('reserved',)).fetchall()
    for (request_id,) in rows:
        path=root/'requests'/request_id/'record.json'
        if not path.exists():
            raise RuntimeError('Unresolved reservation requires reconciliation: '+request_id)
        finalize(root,request_id,json.loads(path.read_text()))
    fingerprint=hashlib.sha256(key.encode()).hexdigest()
    with sqlite3.connect(root/'ledger.sqlite',timeout=30) as db:
        old=db.execute('SELECT value FROM settings WHERE key="credential_fingerprint"').fetchone()
        if old and old[0]!=fingerprint:
            raise RuntimeError('Credentials changed since calibration; account reconciliation required.')
        db.execute('INSERT OR IGNORE INTO settings VALUES (?,?)',('credential_fingerprint',fingerprint))
        halted=db.execute('SELECT value FROM settings WHERE key="halt"').fetchone()
        unresolved=db.execute('SELECT id FROM requests WHERE state NOT IN '
                              '("completed","failed_transport") LIMIT 1').fetchone()
        if halted or unresolved:
            raise RuntimeError('Ledger requires reconciliation before new dispatch.')


def reserve(root, request_id, body):
    encoded = json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    input_bound, maximum = reservation(body)
    with sqlite3.connect(Path(root) / 'ledger.sqlite', timeout=30) as db:
        db.execute('BEGIN IMMEDIATE')
        halted = db.execute('SELECT value FROM settings WHERE key="halt"').fetchone()
        if halted:
            raise RuntimeError('Dispatch halted pending reconciliation: '+halted[0])
        old = db.execute('SELECT request_sha256,state FROM requests WHERE id=?',
                         (request_id,)).fetchone()
        if old:
            if old[0] != digest:
                raise RuntimeError('A request ID was reused with different content.')
            return None
        db.execute('INSERT INTO requests '
                   '(id,request_sha256,state,reserved,model,started) VALUES (?,?,?,?,?,?)',
                   (request_id,digest,'reserved',maximum,body['model'],now()))
    return input_bound, maximum


def extract_answer(text):
    fenced=re.fullmatch(r'\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n```\s*',text,re.DOTALL|re.IGNORECASE)
    if fenced:
        text=fenced[1]
    value = json.loads(text)
    if (not isinstance(value,dict) or set(value) != {'answer','reason','evidence_quote'}
        or value['answer'] not in ('A','B','ABSTAIN')
        or not isinstance(value['reason'],str)
        or (value['evidence_quote'] is not None and not isinstance(value['evidence_quote'],str))):
        raise ValueError('Answer schema mismatch')
    return value


def read_stream(response, folder):
    data = []
    for line in response:
        if line.startswith(b'data:'):
            data.append(line[5:].lstrip().rstrip(b'\r\n'))
        elif not line.strip() and data:
            payload = b'\n'.join(data)
            data = []
            if payload == b'[DONE]':
                break
            event = json.loads(payload)
            if event.get('type') == 'error':
                (folder/'response-event.json').write_bytes(payload)
                raise RuntimeError('Provider stream error')
            if event.get('type') in ('response.completed', 'response.incomplete', 'response.failed'):
                (folder/'response-event.json').write_bytes(payload)
                if not isinstance(event.get('response'), dict):
                    raise RuntimeError('Stream terminal event has no response')
                return event['response']
    raise RuntimeError('Stream ended without a terminal response or usage')


def call(root, key, request_id, body, metadata=None):
    global _LAST_DISPATCH, _RATE_LIMIT_UNTIL
    root = Path(root)
    if root.resolve() != EXECUTION_ROOT.resolve():
        raise RuntimeError('Paid requests must use the package execution ledger.')
    reserved = reserve(root,request_id,body)
    if reserved is None:
        path = root / 'requests' / request_id / 'record.json'
        if path.exists():
            record = json.loads(path.read_text())
            finalize(root,request_id,record)
            return record
        raise RuntimeError('Previously reserved request is unresolved; will not repeat it.')
    input_bound, maximum = reserved
    folder = root / 'requests' / request_id
    save(folder / 'request.json',body)
    record = dict(id=request_id,metadata=metadata or {},started=now(),
                  reserved_credits=maximum,input_bound=input_bound,charged_credits=None,
                  answer=None,error=None,fatal=False,http_status=None)
    started = time.monotonic()
    raw = b''
    result = None
    try:
        while True:
            with _DISPATCH_LOCK:
                delay = max(_LAST_DISPATCH + DISPATCH_SPACING_SECONDS,
                            _RATE_LIMIT_UNTIL) - time.monotonic()
                if delay <= 0:
                    _LAST_DISPATCH = time.monotonic()
                    break
            time.sleep(delay)
        record['dispatched'] = now()
        request = urllib.request.Request(API+'/responses',method='POST',
            data=json.dumps(body,ensure_ascii=False).encode(),headers={
                'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=180) as response:
                record['http_status'] = response.status
                result = read_stream(response, folder)
                raw = json.dumps(result, ensure_ascii=False).encode()
        except urllib.error.HTTPError as exc:
            record['http_status'] = exc.code
            raw = exc.read()
            if exc.code in (502, 503, 504):
                retry_after = (exc.headers or {}).get('Retry-After', '')
                wait_seconds = max(60, int(retry_after) if retry_after.isdigit() else 60)
                record['gateway_backoff_seconds'] = wait_seconds
                with _DISPATCH_LOCK:
                    _RATE_LIMIT_UNTIL = max(_RATE_LIMIT_UNTIL, time.monotonic() + wait_seconds)
            if exc.code == 429:
                try:
                    error = json.loads(raw).get('error', {})
                    if error.get('code') == 'rate_limit_exceeded':
                        seconds = re.search(r'retry after (\d+) seconds', error.get('message', ''), re.I)
                        wait_seconds = max(60, int(seconds[1]) if seconds else 60)
                        retry_after = (exc.headers or {}).get('Retry-After', '')
                        if retry_after.isdigit():wait_seconds = max(wait_seconds, int(retry_after))
                        record['rate_limit_wait_seconds'] = wait_seconds
                        with _DISPATCH_LOCK:
                            _RATE_LIMIT_UNTIL = max(_RATE_LIMIT_UNTIL, time.monotonic() + wait_seconds)
                except (ValueError, TypeError, AttributeError):
                    pass
            raise RuntimeError('HTTP '+str(exc.code)) from None
        record['reported_model'] = result.get('model')
        record['response_status'] = result.get('status')
        record['incomplete_details'] = result.get('incomplete_details')
        record['usage'] = result.get('usage')
        usage = record['usage']
        if not isinstance(usage,dict):
            raise RuntimeError('Missing token accounting')
        inp, out = usage.get('input_tokens'),usage.get('output_tokens')
        cached = (usage.get('input_tokens_details') or {}).get('cached_tokens',0)
        if (not isinstance(inp,int) or not isinstance(out,int) or not isinstance(cached,int)
            or min(inp,out,cached)<0 or cached>inp):
            raise RuntimeError('Invalid token accounting')
        charge = estimated_charge(body['model'],inp,out,cached)
        reported_cost = Decimal(str(usage.get('cost')))
        if not reported_cost.is_finite() or reported_cost < 0:
            raise RuntimeError('Invalid reported credit cost')
        record['published_rate_estimate_credits'] = charge
        charge = max(charge, float(reported_cost.quantize(Decimal('0.000001'), rounding=ROUND_CEILING)))
        if result.get('model') != body['model']:
            raise RuntimeError('Unexpected reported model')
        record['charged_credits'] = charge
        if inp>input_bound or out>body['max_output_tokens']:
            raise RuntimeError('Token usage exceeded request assumptions')
        if any(x.get('type') not in ('message','reasoning') for x in result.get('output',[])):
            raise RuntimeError('Unexpected response item or tool activity')
        text = result.get('output_text')
        if not isinstance(text,str):
            text = ''.join(c.get('text','') for item in result.get('output',[])
                           if item.get('type')=='message' for c in item.get('content',[])
                           if c.get('type')=='output_text')
        record['output_text'] = text
        if result.get('status') not in ('completed','incomplete'):
            raise RuntimeError('Provider response status: '+str(result.get('status')))
        if result.get('status') == 'incomplete':
            record['error'] = 'response_'+str(result.get('status'))
        else:
            try:
                record['answer'] = extract_answer(text)
            except (ValueError,TypeError,AttributeError):
                record['error'] = 'invalid_answer'
    except Exception as exc:
        record['error'] = str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__
        record['fatal'] = True
    record['duration_seconds'] = round(time.monotonic()-started,3)
    record['finished'] = now()
    (folder/'response.json').write_bytes(raw)
    save(folder/'record.json',record)
    finalize(root,request_id,record)
    return record


def finalize(root,request_id,record):
    transport = transport_failure(record)
    charged = record['charged_credits']
    if record['fatal'] and not transport and charged is not None:
        charged = max(charged,record['reserved_credits'])
    with sqlite3.connect(root/'ledger.sqlite',timeout=30) as db:
        if record['fatal'] and not transport:
            db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)',
                       ('halt',request_id+': '+record['error']))
        db.execute('UPDATE requests SET state=?,charged=?,finished=?,error=? WHERE id=?',
                   ('failed_transport' if transport else 'unresolved' if record['fatal'] else 'completed',charged,
                    record['finished'],record['error'],request_id))


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['models','status'])
    parser.add_argument('--root',default='outputs/multi-model-followup/execution')
    parser.add_argument('--key-file',default='work/adaption/private.env')
    args=parser.parse_args()
    initialize(args.root)
    if args.action=='models':
        value=models(key_from_file(args.key_file))
        save(Path(args.root)/'models.json',value)
        print(json.dumps(value,indent=2))
    else:
        print(json.dumps(totals(args.root),indent=2))
