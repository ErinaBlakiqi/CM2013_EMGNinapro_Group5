# Re-running the existing feature experiments on S1–S10

The S1–S10 rerun completed on 2026-11-15 with 27,575 E1 windows. See
[FEATURE_EXPERIMENTS.md](FEATURE_EXPERIMENTS.md#s1s10-rerun) for the results
and the earlier S1–S5 comparison.

## Scope

Repeat only the existing baseline (50 features), RMS ablation (40 features) and
baseline + IQR (60 features). Correlation and per-subject analysis describe these
same feature sets. No new feature methods or parameter search are included.
Preprocessing remains none, selection remains none and seed remains 0. The existing
classifier, feature definitions, CV loops and metrics are unchanged.

Agree the same dataset, settings and evaluation procedure with the team before
comparing these results with preprocessing or model experiments. Final hold-out
subjects S23–S27 are not used.

## Data and output folders

Use an external folder containing exactly one E1 recording per subject S1–S10.
The default with --subjects 10 is ~/cm2013_data/train_s1_s10. This folder is separate
from the earlier S1–S5 folder ~/cm2013_data/train. --data-dir can select another
external folder, but extra/missing subjects and duplicate E1 recordings are rejected
before loading. No data is downloaded by the experiment scripts.

The default output folder is ~/cm2013_data/experiment_results/s1_s10. With
--subjects 5 the existing five-subject cohort remains available and output defaults
to experiment_results/s1_s5. Existing result files in other folders are untouched.

## Run one experiment at a time

In PowerShell, from the repository root with the project .venv active:

```powershell
$runOutput = Join-Path $HOME "cm2013_data\experiment_results\s1_s10"
New-Item -ItemType Directory -Force -Path $runOutput | Out-Null
$env:MPLBACKEND = "Agg"
python -u experiment_rms.py --subjects 10 2>&1 | Tee-Object -FilePath (Join-Path $runOutput "rms_run.txt")
python -u experiment_correlation.py --subjects 10 2>&1 | Tee-Object -FilePath (Join-Path $runOutput "correlation_run.txt")
python -u experiment_iqr.py --subjects 10 2>&1 | Tee-Object -FilePath (Join-Path $runOutput "iqr_run.txt")
python -u experiment_iqr_subjects.py --subjects 10 2>&1 | Tee-Object -FilePath (Join-Path $runOutput "iqr_subjects_run.txt")
```

Run each command only after the previous one finishes successfully. The RMS and IQR
scripts each run their own unchanged baseline for the paired comparison; this does
not introduce another configuration. The correlation/per-subject scripts save CSV
and PNG files in the selected output folder. RMS/IQR reports are saved by Tee-Object.
Use a new output directory if repeating this batch, so earlier logs are not replaced.

Before reporting, retain the code commit, Python/library versions, input-file hashes,
subject/window counts, config and per-subject scores. Compare both evaluation modes
and distinguish pooled scores from subject means and SD. Document new S1–S10 results
separately; do not interpret a difference from S1–S5 as a feature improvement.
