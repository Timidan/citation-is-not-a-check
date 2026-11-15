# Right Report, Wrong Row

Code and data for *Right Report, Wrong Row: Without the Source Text, Three LLMs Follow Misleading Corrections* (Temitayo Daniel, independent researcher), written at the Apart Research AI x Epistemics Research Sprint, 13–15 November 2026. The paper is in [`paper/right-report-wrong-row.pdf`](paper/right-report-wrong-row.pdf).

120 two-option questions from EIA, BLS, UNESCO and World Bank tables, where both options are real values from the same table. Three hosted models (Qwen 3.8-27B, GLM 5.3 Flash, DeepSeek V4 Flash, served by Adaption) answered each question in twelve conditions: citation only or citation plus table excerpt, with a correct or incorrect draft answer, with or without a valid or misleading user correction, and with or without an instruction to check the source. A separate experiment challenged each model's own earlier answer. With only the citation, the models followed the user's correction in both directions and almost never abstained; with the excerpt, no usable answer accepted a misleading correction.

## Contents

| Path | What it holds |
|---|---|
| `frozen/` | The frozen study: questions and answer keys (`cases.json`), the 4,320-prompt schedule, the own-answer schedule, model settings, protocol with dated amendments, and the scripts. `manifest.json` gives SHA-256 hashes of every file. |
| `data/requests/<id>/` | One folder per core request (5,390): the exact request body, the model's response, and the parsed record used for scoring. |
| `results/` | Analysis output: per-cell counts and contrasts (`analysis.json`), one row per scheduled prompt (`scheduled-outcomes.csv`), own-answer pairs, the results report and the request audit. |
| `sources/` | Archived source snapshots, item selections and selection audits for the four statistical sources. |
| `paper/` | The submitted report. |

## Reproduce the analysis

Python 3, standard library only:

```bash
python3 frozen/analyze_study.py --frozen frozen --root data --out out
```

`out/analysis.json` matches `results/analysis.json` in every section except `ledger`, which summarizes billing from a private ledger that is not released.

Rerunning inference needs an Adaption API key (`ADAPTION_API_KEY`) and `frozen/run_study.py`. The scripts are byte-identical to the frozen versions, so `PACKAGE_ROOT` in `adaption_client.py` still points at the original local folder; change it before running.

## What is not included

- Provider response IDs and per-request credit charges, which were removed from the records.
- The billing ledger and account records.
- Extra repetitions and a 40-question SEC extension collected before the scope was cut to one repetition. They are exploratory and are not used in the paper.
- An earlier NOAA pilot and the technical calibration calls.

## Notes

All code, the question set, data collection and analysis were produced during the sprint. AI assistants (OpenAI Codex, Anthropic Claude, Google Antigravity) helped with planning, code, analysis and writing; see the paper's LLM Usage Statement. Source tables belong to their publishers (U.S. EIA, U.S. BLS, UNESCO Institute for Statistics, World Bank) and are included as archived snapshots for verification.
