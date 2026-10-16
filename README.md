# Food Inspection Risk Prioritizer

Train a chronologically held-out failure-risk baseline to help analysts review inspection workloads.

> **Portfolio prototype.** Source code is provided; no benchmark results are claimed until you run it on the cited data and record the output.

## Use case

Train a chronologically held-out failure-risk baseline to help analysts review inspection workloads. The CLI consumes local files, emits reproducible reports, and keeps data out of the repository.

## Data and provenance

[City of Chicago Food Inspections open dataset](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5). Chicago inspection CSV with Inspection Date and Results. Excludes inspection outcomes, violation text, business identifiers, and free-text fields from model features. Source files are not bundled. Respect source terms and cite the dataset when publishing results.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Download/prepare the source data locally, then run:
python main.py --input data/food_inspections.csv --date 'Inspection Date' --result Results --out outputs
```

## Outputs

Generated results are saved under `outputs/`; file names and metrics are printed or documented by the CLI. The repository excludes downloaded data and artifacts.

## Evaluation and operating notes

This is a retrospective exploratory model, not an enforcement recommendation. Public inspection records have selection and reporting bias; human review and current local criteria must govern decisions.

For production use, add a frozen reference period, out-of-time evaluation, monitoring ownership, and a documented rollback or escalation path. This project is a local baseline, not a deployed service.

## License

No code license file is included yet. Third-party data remains subject to its source terms.
