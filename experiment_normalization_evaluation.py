"""Iteration 4 - downstream classification of the registered normalization comparison.

Compares the identity baseline against P1 (per-window, per-channel RMS
normalization) and P2 (per-window global RMS normalization) on Ninapro DB1 E1.
Only preprocess changes; features, selection, classifier and seed are unchanged.
Both required evaluation modes are run on the same folds:
  - within-subject: repetition-grouped CV inside each subject
  - new-subject:    subject-grouped CV (subjects never span train and test)

Outputs (in --output-dir):
  normalization_eval_summary.csv     pooled + per-subject spread per config/mode
  normalization_eval_per_subject.csv per-subject macro-F1 with paired change vs baseline
"""
import csv
import platform
import sys

import numpy as np
import sklearn

from emg_ninapro import EMGNinaproTrack
from experiment_common import arguments, load_development

CONFIGS = [
    ("Baseline (identity)", "none"),
    ("P1 per-channel window RMS", "rms_per_channel"),
    ("P2 global window RMS", "rms_global"),
]
MODES = ("within_subject", "new_subject")
METRICS = ("macro_f1", "cohens_kappa", "balanced_accuracy", "accuracy")


def per_subject_f1(report):
    return {row["group"]: float(row["macro_f1"]) for row in report["per_group"]}


def main(argv=None):
    args = arguments(__doc__, argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print("Python", platform.python_version(), "| numpy", np.__version__,
          "| scikit-learn", sklearn.__version__)

    track = EMGNinaproTrack()
    recs = load_development(track, args.data_dir, args.subjects)

    results = {}
    for name, method in CONFIGS:
        cfg = {"preprocess": method, "select": "none", "seed": 0}
        print(f"\nRunning {name} with cfg={cfg} ...", flush=True)
        results[name] = track.evaluate_modes(recs, cfg=cfg)
        for mode in MODES:
            rep = results[name][mode]
            print(f"  {mode}: pooled macro-F1 {rep['macro_f1']:.3f}, "
                  f"kappa {rep['cohens_kappa']:.3f}, "
                  f"balanced acc {rep['balanced_accuracy']:.3f}")
            print(f"    {rep['summary']}")

    base_name = CONFIGS[0][0]
    summary_rows, subject_rows = [], []
    for name, _ in CONFIGS:
        for mode in MODES:
            rep = results[name][mode]
            sp = rep["spread"]["macro_f1"]
            row = {"config": name, "mode": mode}
            row.update({f"pooled_{m}": round(float(rep[m]), 4) for m in METRICS})
            row.update({"subject_mean_macro_f1": round(float(sp.get("mean", np.nan)), 4),
                        "subject_sd_macro_f1": round(float(sp.get("std", np.nan)), 4),
                        "subject_min_macro_f1": round(float(sp.get("min", np.nan)), 4),
                        "subject_max_macro_f1": round(float(sp.get("max", np.nan)), 4)})
            summary_rows.append(row)

            base = per_subject_f1(results[base_name][mode])
            this = per_subject_f1(rep)
            for subj in sorted(this, key=lambda g: int(str(g)[1:])):
                subject_rows.append({
                    "config": name, "mode": mode, "subject": subj,
                    "macro_f1": round(this[subj], 4),
                    "change_vs_baseline": round(this[subj] - base[subj], 4)})

    # Paired view: how many subjects improved, and mean paired change.
    print("\nPaired per-subject change in macro-F1 vs baseline")
    for name, _ in CONFIGS[1:]:
        for mode in MODES:
            d = [r["change_vs_baseline"] for r in subject_rows
                 if r["config"] == name and r["mode"] == mode]
            print(f"  {name:28s} {mode:15s} mean {np.mean(d):+.4f} "
                  f"(sd {np.std(d, ddof=1):.4f}); improved {sum(x > 0 for x in d)}/{len(d)}")

    for fname, rows in (("normalization_eval_summary.csv", summary_rows),
                        ("normalization_eval_per_subject.csv", subject_rows)):
        path = args.output_dir / fname
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print("Saved", path)


if __name__ == "__main__":
    sys.exit(main())
