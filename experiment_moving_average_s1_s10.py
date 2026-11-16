"""Consistency rerun: 3-sample causal moving average vs identity baseline on S1-S10.

The moving average (Iteration 2) was only evaluated on S1-S5. This reruns the
SAME configuration on the S1-S10 development set with the same setup as the
P1/P2 comparison (all 27,575 windows, 50 baseline features, select="none",
default Random Forest, seed 0, identical folds), so every preprocessing result
is reported on the same subjects. It is not a new configuration.

Outputs (in --output-dir): moving_average_s1_s10_summary.csv,
moving_average_s1_s10_per_subject.csv
"""
import csv
import sys

import numpy as np

from emg_ninapro import EMGNinaproTrack
from experiment_common import arguments, load_development

CONFIGS = [("Baseline (identity)", "none"),
           ("Moving average (3-sample causal)", "moving_average")]
MODES = ("within_subject", "new_subject")
METRICS = ("macro_f1", "cohens_kappa", "balanced_accuracy", "accuracy")


def per_subject_f1(report):
    return {row["group"]: float(row["macro_f1"]) for row in report["per_group"]}


def main(argv=None):
    args = arguments(__doc__, argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
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
                  f"kappa {rep['cohens_kappa']:.3f}, balanced acc {rep['balanced_accuracy']:.3f}")
            print(f"    {rep['summary']}")

    base_name, ma_name = CONFIGS[0][0], CONFIGS[1][0]
    summary_rows, subject_rows = [], []
    for name, _ in CONFIGS:
        for mode in MODES:
            rep = results[name][mode]
            sp = rep["spread"]["macro_f1"]
            row = {"config": name, "mode": mode}
            row.update({f"pooled_{m}": round(float(rep[m]), 4) for m in METRICS})
            row.update({"subject_mean_macro_f1": round(sp["mean"], 4),
                        "subject_sd_macro_f1": round(sp["std"], 4),
                        "subject_min_macro_f1": round(sp["min"], 4),
                        "subject_max_macro_f1": round(sp["max"], 4)})
            summary_rows.append(row)
            base, this = per_subject_f1(results[base_name][mode]), per_subject_f1(rep)
            for s in sorted(this, key=lambda g: int(str(g)[1:])):
                subject_rows.append({"config": name, "mode": mode, "subject": s,
                                     "macro_f1": round(this[s], 4),
                                     "change_vs_baseline": round(this[s] - base[s], 4)})

    print("\nPaired per-subject change in macro-F1, moving average vs baseline (same folds)")
    for mode in MODES:
        d = np.array([r["change_vs_baseline"] for r in subject_rows
                      if r["config"] == ma_name and r["mode"] == mode])
        sd = d.std(ddof=1)
        se = sd / np.sqrt(len(d))
        ratio = f"{d.mean() / se:+.2f}" if se > 0 else "n/a (identical scores)"
        print(f"  {mode:15s} mean {d.mean():+.4f} (sd {sd:.4f}, SE {se:.4f}, mean/SE {ratio}); "
              f"improved {int((d > 0).sum())}/{len(d)}, worse {int((d < 0).sum())}/{len(d)}")

    for fname, rows in (("moving_average_s1_s10_summary.csv", summary_rows),
                        ("moving_average_s1_s10_per_subject.csv", subject_rows)):
        path = args.output_dir / fname
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print("Saved", path)


if __name__ == "__main__":
    sys.exit(main())
