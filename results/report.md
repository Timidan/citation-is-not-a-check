# Balanced core results

The revised primary schedule contains 120 questions, three hosted aliases, twelve conditions and one original repetition: 4,320 main calls. This scope amendment was made after collection began. Extra repetitions and the SEC extension are retained separately. All primary entries below were attempted; failures remain in the denominators.

## Main outcomes

| Model | Correct | Incorrect | Abstain | Incomplete | Invalid output | Operational failure |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 3.8-27B | 1074 | 197 | 25 | 136 | 2 | 6 |
| GLM 5.3 Flash | 974 | 126 | 41 | 133 | 15 | 151 |
| DeepSeek V4 Flash | 1151 | 218 | 14 | 8 | 5 | 44 |

Each model has 1,440 scheduled calls. Operational failure includes provider errors and a locally interrupted attempt where applicable. These counts do not imply that every attempt produced a usable model answer.

## Accuracy by condition

Each value is correct / 120 scheduled items.

| Condition | Qwen | GLM | DeepSeek |
|---|---:|---:|---:|
| QA with citation | 43/120 | 43/120 | 75/120 |
| QA with excerpt | 120/120 | 102/120 | 116/120 |
| Correct draft with citation | 64/120 | 70/120 | 101/120 |
| Incorrect draft with citation | 19/120 | 26/120 | 46/120 |
| Correct draft with excerpt | 119/120 | 106/120 | 114/120 |
| Incorrect draft with excerpt | 119/120 | 101/120 | 114/120 |
| Valid correction with citation | 100/120 | 91/120 | 115/120 |
| Misleading correction with citation | 12/120 | 9/120 | 7/120 |
| Valid correction with excerpt | 120/120 | 112/120 | 117/120 |
| Misleading correction with excerpt | 119/120 | 107/120 | 114/120 |
| Valid correction with excerpt and check | 119/120 | 108/120 | 116/120 |
| Misleading correction with excerpt and check | 120/120 | 99/120 | 116/120 |

## Primary contrasts and controls

Values are differences in scheduled-call accuracy, in percentage points. The core has equal numbers from each family. No pooled confidence interval is claimed.

| Contrast | Qwen | GLM | DeepSeek |
|---|---:|---:|---:|
| valid challenge citation | +67.5 | +54.2 | +57.5 |
| valid challenge source | +0.8 | +9.2 | +2.5 |
| misleading challenge citation | -43.3 | -50.8 | -78.3 |
| misleading challenge source | +0.0 | +0.8 | +0.0 |
| ordinary qa source gain | +64.2 | +49.2 | +34.2 |
| valid check instruction | -0.8 | -3.3 | -0.8 |
| misleading check instruction | +0.8 | -6.7 | +1.7 |
| valid evidence interaction | -66.7 | -45.0 | -55.0 |
| misleading evidence interaction | +43.3 | +51.7 | +78.3 |

## Successful response sensitivity

The denominator includes correct, incorrect and ABSTAIN schema-valid answers, excluding incomplete, invalid and operational failures. This conditional view may select easier cases.

| Condition | Qwen | GLM | DeepSeek |
|---|---:|---:|---:|
| QA with citation | 43/79 | 43/83 | 75/116 |
| QA with excerpt | 120/120 | 102/102 | 116/116 |
| Correct draft with citation | 64/90 | 70/81 | 101/117 |
| Incorrect draft with citation | 19/80 | 26/74 | 46/111 |
| Correct draft with excerpt | 119/119 | 106/106 | 114/114 |
| Incorrect draft with excerpt | 119/119 | 101/101 | 114/114 |
| Valid correction with citation | 100/103 | 91/92 | 115/116 |
| Misleading correction with citation | 12/108 | 9/76 | 7/116 |
| Valid correction with excerpt | 120/120 | 112/112 | 117/117 |
| Misleading correction with excerpt | 119/119 | 107/107 | 114/114 |
| Valid correction with excerpt and check | 119/119 | 108/108 | 116/116 |
| Misleading correction with excerpt and check | 120/120 | 99/99 | 116/116 |

## Own answers

Initial calls scheduled: 360. Eligible pairs: 355. Revision calls skipped for ineligible initial responses: 10.

| Model | Initial outcome counts |
|---|---|
| Qwen 3.8-27B | correct: 120 |
| GLM 5.3 Flash | correct: 119, invalid_output: 1 |
| DeepSeek V4 Flash | correct: 116, invalid_output: 4 |

Paired rows use all eligible initial responses. An attempted but failed revision is not correct; both-valid counts show attrition.

| Model and initial answer | Pairs | Neutral correct | Challenged correct | Both valid | Change pp |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 3.8-27B initially correct | 120 | 120/120 | 116/120 | 116 | -3.3 |
| Qwen 3.8-27B initially incorrect | 0 | Not applicable | Not applicable | 0 | Not applicable |
| GLM 5.3 Flash initially correct | 119 | 119/119 | 112/119 | 112 | -5.9 |
| GLM 5.3 Flash initially incorrect | 0 | Not applicable | Not applicable | 0 | Not applicable |
| DeepSeek V4 Flash initially correct | 116 | 116/116 | 115/116 | 115 | -0.9 |
| DeepSeek V4 Flash initially incorrect | 0 | Not applicable | Not applicable | 0 | Not applicable |

## Source family results

Conditional EIA/BLS intervals resample the retained state documents and omit shared-program dependence. UNESCO and WDI results remain descriptive. Repetitions are not independent sources; there is only one core repetition.

### Qwen 3.8-27B

| Family | Contrast | Difference pp | Conditional document interval pp |
|---|---|---:|---|
| eia | valid challenge citation | +40.0 | +20.0 to +60.0 |
| eia | valid challenge source | +0.0 | +0.0 to +0.0 |
| eia | misleading challenge citation | -26.7 | -43.3 to -10.0 |
| eia | misleading challenge source | +3.3 | +0.0 to +10.0 |
| eia | ordinary qa source gain | +63.3 | +46.7 to +80.0 |
| eia | valid check instruction | -3.3 | -10.0 to +0.0 |
| eia | misleading check instruction | +0.0 | +0.0 to +0.0 |
| eia | valid evidence interaction | -40.0 | -60.0 to -20.0 |
| eia | misleading evidence interaction | +30.0 | +13.3 to +50.0 |
| bls | valid challenge citation | +90.0 | +73.3 to +100.0 |
| bls | valid challenge source | +0.0 | +0.0 to +0.0 |
| bls | misleading challenge citation | -40.0 | -56.7 to -23.3 |
| bls | misleading challenge source | -3.3 | -10.0 to +0.0 |
| bls | ordinary qa source gain | +66.7 | +50.0 to +83.3 |
| bls | valid check instruction | +0.0 | +0.0 to +0.0 |
| bls | misleading check instruction | +3.3 | +0.0 to +10.0 |
| bls | valid evidence interaction | -90.0 | -100.0 to -76.7 |
| bls | misleading evidence interaction | +36.7 | +20.0 to +53.3 |
| unesco | valid challenge citation | +86.7 | Not estimated |
| unesco | valid challenge source | +0.0 | Not estimated |
| unesco | misleading challenge citation | -66.7 | Not estimated |
| unesco | misleading challenge source | +0.0 | Not estimated |
| unesco | ordinary qa source gain | +76.7 | Not estimated |
| unesco | valid check instruction | +0.0 | Not estimated |
| unesco | misleading check instruction | +0.0 | Not estimated |
| unesco | valid evidence interaction | -86.7 | Not estimated |
| unesco | misleading evidence interaction | +66.7 | Not estimated |
| worldbank | valid challenge citation | +53.3 | Not estimated |
| worldbank | valid challenge source | +3.3 | Not estimated |
| worldbank | misleading challenge citation | -40.0 | Not estimated |
| worldbank | misleading challenge source | +0.0 | Not estimated |
| worldbank | ordinary qa source gain | +50.0 | Not estimated |
| worldbank | valid check instruction | +0.0 | Not estimated |
| worldbank | misleading check instruction | +0.0 | Not estimated |
| worldbank | valid evidence interaction | -50.0 | Not estimated |
| worldbank | misleading evidence interaction | +40.0 | Not estimated |
### GLM 5.3 Flash

| Family | Contrast | Difference pp | Conditional document interval pp |
|---|---|---:|---|
| eia | valid challenge citation | +43.3 | +23.3 to +63.3 |
| eia | valid challenge source | +10.0 | -6.7 to +26.7 |
| eia | misleading challenge citation | -46.7 | -66.7 to -30.0 |
| eia | misleading challenge source | +13.3 | +0.0 to +30.0 |
| eia | ordinary qa source gain | +36.7 | +16.7 to +56.7 |
| eia | valid check instruction | +0.0 | -13.3 to +13.3 |
| eia | misleading check instruction | -13.3 | -26.7 to -3.3 |
| eia | valid evidence interaction | -33.3 | -60.0 to -10.0 |
| eia | misleading evidence interaction | +60.0 | +36.7 to +86.7 |
| bls | valid challenge citation | +36.7 | +16.7 to +56.7 |
| bls | valid challenge source | +16.7 | +3.3 to +30.0 |
| bls | misleading challenge citation | -43.3 | -60.0 to -26.7 |
| bls | misleading challenge source | -10.0 | -26.7 to +6.7 |
| bls | ordinary qa source gain | +33.3 | +10.0 to +56.7 |
| bls | valid check instruction | -3.3 | -10.0 to +0.0 |
| bls | misleading check instruction | +0.0 | -20.0 to +20.0 |
| bls | valid evidence interaction | -20.0 | -40.0 to +0.0 |
| bls | misleading evidence interaction | +33.3 | +10.0 to +56.7 |
| unesco | valid challenge citation | +80.0 | Not estimated |
| unesco | valid challenge source | +0.0 | Not estimated |
| unesco | misleading challenge citation | -60.0 | Not estimated |
| unesco | misleading challenge source | +3.3 | Not estimated |
| unesco | ordinary qa source gain | +80.0 | Not estimated |
| unesco | valid check instruction | +3.3 | Not estimated |
| unesco | misleading check instruction | -10.0 | Not estimated |
| unesco | valid evidence interaction | -80.0 | Not estimated |
| unesco | misleading evidence interaction | +63.3 | Not estimated |
| worldbank | valid challenge citation | +56.7 | Not estimated |
| worldbank | valid challenge source | +10.0 | Not estimated |
| worldbank | misleading challenge citation | -53.3 | Not estimated |
| worldbank | misleading challenge source | -3.3 | Not estimated |
| worldbank | ordinary qa source gain | +46.7 | Not estimated |
| worldbank | valid check instruction | -13.3 | Not estimated |
| worldbank | misleading check instruction | -3.3 | Not estimated |
| worldbank | valid evidence interaction | -46.7 | Not estimated |
| worldbank | misleading evidence interaction | +50.0 | Not estimated |
### DeepSeek V4 Flash

| Family | Contrast | Difference pp | Conditional document interval pp |
|---|---|---:|---|
| eia | valid challenge citation | +43.3 | +26.7 to +60.0 |
| eia | valid challenge source | +3.3 | +0.0 to +10.0 |
| eia | misleading challenge citation | -70.0 | -86.7 to -53.3 |
| eia | misleading challenge source | +0.0 | -10.0 to +10.0 |
| eia | ordinary qa source gain | +26.7 | +10.0 to +46.7 |
| eia | valid check instruction | +0.0 | +0.0 to +0.0 |
| eia | misleading check instruction | +0.0 | -10.0 to +10.0 |
| eia | valid evidence interaction | -40.0 | -60.0 to -20.0 |
| eia | misleading evidence interaction | +70.0 | +50.0 to +90.0 |
| bls | valid challenge citation | +46.7 | +30.0 to +66.7 |
| bls | valid challenge source | +6.7 | -6.7 to +20.0 |
| bls | misleading challenge citation | -86.7 | -96.7 to -73.3 |
| bls | misleading challenge source | -3.3 | -16.7 to +6.7 |
| bls | ordinary qa source gain | +46.7 | +30.0 to +66.7 |
| bls | valid check instruction | -3.3 | -13.3 to +6.7 |
| bls | misleading check instruction | +0.0 | -13.3 to +13.3 |
| bls | valid evidence interaction | -40.0 | -60.0 to -20.0 |
| bls | misleading evidence interaction | +83.3 | +66.7 to +100.0 |
| unesco | valid challenge citation | +96.7 | Not estimated |
| unesco | valid challenge source | +0.0 | Not estimated |
| unesco | misleading challenge citation | -80.0 | Not estimated |
| unesco | misleading challenge source | +0.0 | Not estimated |
| unesco | ordinary qa source gain | +46.7 | Not estimated |
| unesco | valid check instruction | -6.7 | Not estimated |
| unesco | misleading check instruction | +3.3 | Not estimated |
| unesco | valid evidence interaction | -96.7 | Not estimated |
| unesco | misleading evidence interaction | +80.0 | Not estimated |
| worldbank | valid challenge citation | +43.3 | Not estimated |
| worldbank | valid challenge source | +0.0 | Not estimated |
| worldbank | misleading challenge citation | -76.7 | Not estimated |
| worldbank | misleading challenge source | +3.3 | Not estimated |
| worldbank | ordinary qa source gain | +16.7 | Not estimated |
| worldbank | valid check instruction | +6.7 | Not estimated |
| worldbank | misleading check instruction | +3.3 | Not estimated |
| worldbank | valid evidence interaction | -43.3 | Not estimated |
| worldbank | misleading evidence interaction | +80.0 | Not estimated |

## Provenance and remaining distinctions

The active protocol and execution amendments are in the sibling frozen-balanced-core and execution directories. The full original schedule analysis is separate in results-full-schedule-exploratory; it includes unattempted original entries and must not be described as completion of that package. The earlier NOAA paper and AGY technical checks are not pooled. Reported aliases do not identify exact upstream weights. Account reconciliation is separate from the ledger estimate. No independent human source audit or public submission is claimed.

Analysis SHA-256: 37adfc73ae943b35eb7659711537dccb9f553b6294a80fc4c1d9934c5b9f6e63
