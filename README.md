# Food Inspection Risk Prioritizer

A research prototype that ranks inspection records for analyst review using only prior/context fields. It does not label an establishment as unsafe or recommend enforcement.

## Public data and privacy

Uses the [City of Chicago Food Inspections API](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5). The local extract contains only `inspection_id` (for deduplication), inspection date, facility type, risk, inspection type, and outcome. It omits establishment names, addresses, license numbers, violation narratives, and coordinates; the ID is excluded from model features and public output.

The 50,000 most recent records (2024-02-27 through 2026-11-13) were downloaded. Duplicate IDs are removed. Only `Fail`, `Pass`, and `Pass w/ Conditions` are used; `Fail` is the positive class and the latter two are non-fail. Non-completion outcomes (such as `No Entry` and `Out of Business`) are excluded. This explicit label rule leaves 41,777 eligible records.

## Reproduce

Download the selected fields from the official API, then run:

```powershell
$uri = 'https://data.cityofchicago.org/resource/4ijn-s7e5.csv?%24select=inspection_id,inspection_date,facility_type,risk,inspection_type,results&%24where=inspection_date%20%3E=%20%272018-01-01T00:00:00%27&%24order=inspection_date%20DESC&%24limit=50000'
Invoke-WebRequest -Uri $uri -OutFile chicago_inspections.csv
python -m pip install -r requirements.txt
python main.py --input chicago_inspections.csv --date inspection_date --result results --out outputs
```

The runner removes duplicate IDs, excludes the derived target and post-inspection fields from predictors, sorts by date, and splits on unique calendar days so no day crosses train and holdout. Local row-level review queues, the source CSV, and model files are ignored.

## Recent forward holdout

Training ends 2026-04-30; holdout begins 2026-05-01.

| Train | Holdout | Holdout fail rate | ROC-AUC | Average precision |
|---:|---:|---:|---:|---:|
| 34,717 | 7,060 | 21.8% | 0.627 | 0.303 |

The result is modest signal on one limited recent extract. The City/Data.gov catalog warns that duplicate inspection reports may remain and inspection procedures changed in 2018; this run removed duplicate IDs and uses recent post-change data. This does not establish causal risk, current establishment safety, or performance on future inspections. Use only for human review and validate again on a deduplicated, refreshed dataset.

Aggregate metrics and input fingerprint: [`reports/benchmark.json`](reports/benchmark.json).
