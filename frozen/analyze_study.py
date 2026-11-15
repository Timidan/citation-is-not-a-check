"""Deterministic descriptive analysis; scheduled failures remain in denominators."""
from collections import Counter, defaultdict
import argparse
import csv
import json
from pathlib import Path
import random
import statistics
import sqlite3

from adaption_client import save, totals

CONTRASTS={
    'valid_challenge_citation':('valid_citation','draft_wrong_citation'),
    'valid_challenge_source':('valid_source','draft_wrong_source'),
    'misleading_challenge_citation':('misleading_citation','draft_correct_citation'),
    'misleading_challenge_source':('misleading_source','draft_correct_source'),
    'ordinary_qa_source_gain':('qa_source','qa_citation'),
    'valid_check_instruction':('valid_source_check','valid_source'),
    'misleading_check_instruction':('misleading_source_check','misleading_source'),
}


def load_record(root,request_id,reserved):
    path=root/'requests'/request_id/'record.json'
    if path.exists():return json.loads(path.read_text())
    return {'reservation_only':True} if request_id in reserved else None


def category(record,gold):
    if record is None:return 'unattempted'
    if record.get('reservation_only'):return 'unresolved_dispatch'
    if record.get('fatal'):return 'operational_failure'
    if record.get('error')=='response_incomplete':return 'truncated_or_incomplete'
    if record.get('error'):return 'invalid_output'
    answer=(record.get('answer') or {}).get('answer')
    if answer=='ABSTAIN':return 'abstain'
    if answer in ('A','B'):return 'correct' if answer==gold else 'incorrect'
    return 'invalid_output'


def interval(values,seed):
    # Caller supplies one contrast per state/issuer source document.
    rng=random.Random(seed)
    values=list(values)
    draws=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(2000))
    return [draws[49],draws[1949]]


def analyze(frozen,root,out):
    items={i['id']:i for i in json.loads((frozen/'cases.json').read_text())}
    schedule=json.loads((frozen/'schedule.json').read_text())
    own=json.loads((frozen/'own-schedule.json').read_text())
    config=json.loads((frozen/'config.json').read_text())
    reserved=set()
    if (root/'ledger.sqlite').exists():
        with sqlite3.connect(root/'ledger.sqlite') as db:
            reserved={row[0] for row in db.execute('SELECT id FROM requests')}
    rows=[]; groups=defaultdict(Counter); item_scores=defaultdict(list)
    rep_scores=defaultdict(list)
    for entry in schedule:
        item=items[entry['item_id']]
        record=load_record(root,entry['id'],reserved)
        outcome=category(record,item['correct_option'])
        score=int(outcome=='correct')
        key=(entry['model'],item['cohort'],item['family'],entry['cell'])
        groups[key][outcome]+=1
        item_scores[(entry['model'],item['family'],item['id'],entry['cell'])].append(score)
        rep_scores[key+(entry['rep'],)].append(score)
        rows.append(dict(request_id=entry['id'],model=entry['model'],cohort=item['cohort'],
                         family=item['family'],document_id=item['document_id'],item_id=item['id'],
                         rep=entry['rep'],cell=entry['cell'],outcome=outcome,correct=score))
    cells=[]
    for key,counts in sorted(groups.items()):
        n=sum(counts.values()); valid=counts['correct']+counts['incorrect']+counts['abstain']
        reps=[statistics.mean(values) for k,values in rep_scores.items() if k[:4]==key]
        cells.append(dict(zip(['model','cohort','family','cell'],key),scheduled=n,counts=dict(counts),
                          accuracy=counts['correct']/n,
                          successful_response_accuracy=counts['correct']/valid if valid else None,
                          repetition_accuracy_range=[min(reps),max(reps)]))
    contrast_rows=[]
    family_items=defaultdict(list)
    for item in items.values():family_items[item['family']].append(item)
    for model in config['models']:
        family_effects={}
        for family,group in family_items.items():
            effects={}
            for name,(challenged,control) in CONTRASTS.items():
                values=[statistics.mean(item_scores[(model,family,i['id'],challenged)])
                        -statistics.mean(item_scores[(model,family,i['id'],control)]) for i in group]
                effects[name]=values
            for direction in ['valid','misleading']:
                effects[direction+'_evidence_interaction']=[a-b for a,b in zip(
                    effects[direction+'_challenge_source'],effects[direction+'_challenge_citation'])]
            family_effects[family]={name:statistics.mean(v) for name,v in effects.items()}
            for name,values in effects.items():
                ci=interval(values,20261113) if family in ('eia','bls','fifth') else None
                contrast_rows.append(dict(model=model,family=family,contrast=name,
                    accuracy_difference=statistics.mean(values),source_items=len(values),
                    conditional_document_bootstrap_95=ci))
        for name in next(iter(family_effects.values())):
            values=[family_effects[f][name] for f in ['eia','bls','unesco','worldbank']]
            leave=[statistics.mean(values[:i]+values[i+1:]) for i in range(4)]
            contrast_rows.append(dict(model=model,family='main_equal_provider_average',contrast=name,
                accuracy_difference=statistics.mean(values),source_items=120,
                conditional_document_bootstrap_95=None,leave_one_provider_out_range=[min(leave),max(leave)]))
    initial_counts=defaultdict(Counter); own_pairs=defaultdict(list); own_rows=[]
    for entry in own:
        item=items[entry['item_id']]
        first=load_record(root,entry['id']+'-initial',reserved)
        initial_category=category(first,item['correct_option'])
        initial_counts[entry['model']][initial_category]+=1
        if initial_category not in ('correct','incorrect'):continue
        neutral=load_record(root,entry['id']+'-neutral',reserved)
        challenged=load_record(root,entry['id']+'-challenge',reserved)
        nc=category(neutral,item['correct_option']); cc=category(challenged,item['correct_option'])
        pair=dict(id=entry['id'],model=entry['model'],family=item['family'],item_id=item['id'],
                  rep=entry['rep'],initial=initial_category,neutral=nc,challenge=cc,
                  accuracy_difference=int(cc=='correct')-int(nc=='correct'),
                  both_attempted=nc not in ('unattempted','unresolved_dispatch') and cc not in ('unattempted','unresolved_dispatch'),
                  both_valid=nc in ('correct','incorrect','abstain') and cc in ('correct','incorrect','abstain'))
        own_rows.append(pair)
        own_pairs[(entry['model'],item['family'],initial_category)].append(pair)
        own_pairs[(entry['model'],'all_main',initial_category)].append(pair)
    own_effects=[]
    for (model,family,stratum),pairs in sorted(own_pairs.items()):
        by_item=defaultdict(list); complete_by_item=defaultdict(list)
        for pair in pairs:
            by_item[pair['item_id']].append(pair['accuracy_difference'])
            if pair['both_attempted']:complete_by_item[pair['item_id']].append(pair['accuracy_difference'])
        own_effects.append(dict(model=model,family=family,initial=stratum,eligible_pairs=len(pairs),
            source_items=len(by_item),both_attempted=sum(p['both_attempted'] for p in pairs),
            both_valid=sum(p['both_valid'] for p in pairs),
            accuracy_difference=statistics.mean(statistics.mean(v) for v in by_item.values()),
            complete_pair_accuracy_difference=(statistics.mean(statistics.mean(v) for v in complete_by_item.values())
                                            if complete_by_item else None),
            neutral_outcomes=dict(Counter(p['neutral'] for p in pairs)),
            challenge_outcomes=dict(Counter(p['challenge'] for p in pairs))))
    ledger=totals(root) if (root/'ledger.sqlite').exists() else {'accounted_credits':0,'states':{}}
    result=dict(status='descriptive_analysis',scheduled_main_and_fifth=len(schedule),
                main_and_fifth_outcomes=dict(Counter(r['outcome'] for r in rows)),
                own_initial_scheduled=len(own),own_initial_outcomes={m:dict(c) for m,c in initial_counts.items()},
                own_eligible_pairs=len(own_rows),
                own_revision_skipped_ineligible=2*sum(c[k] for c in initial_counts.values() for k in ('abstain','invalid_output','truncated_or_incomplete','operational_failure')),
                own_revision_pending_initial=2*sum(c[k] for c in initial_counts.values() for k in ('unattempted','unresolved_dispatch')),
                cells=cells,contrasts=contrast_rows,own_answer_effects=own_effects,ledger=ledger,
                limitations='Conditional state/issuer intervals omit shared-program dependence. No pooled CI; UNESCO/WDI descriptive only. All costs are usage estimates or unresolved reservations until reconciled to billing.')
    save(out/'analysis.json',result)
    out.mkdir(parents=True,exist_ok=True)
    for name,values in [('scheduled-outcomes.csv',rows),('own-answer-pairs.csv',own_rows)]:
        if values:
            with (out/name).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
    return {k:v for k,v in result.items() if k not in ('cells','contrasts','own_answer_effects')}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent/'execution')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(analyze(a.frozen,a.root,a.out),indent=2))
