"""Noise floor: how much does the baseline score move when nothing changes?

Runs the unchanged baseline (preprocess="none", select="none", 50 features,
default Random Forest) with seeds 0-4 on the same folds, in both evaluation
modes. Only the random seed of the classifier changes, so the spread across
seeds is the run-to-run noise. A preprocessing/feature/model difference smaller
than this (or smaller than the across-subject SD) is not a measurable improvement.

Output: seed_noise_summary.csv in --output-dir.
"""
import csv
import sys

import numpy as np

from emg_ninapro import EMGNinaproTrack
from experiment_common import arguments, load_development

SEEDS = (0, 1, 2, 3, 4)
MODES = ("within_subject", "new_subject")


def main(argv=None):
    args = arguments(__doc__, argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    track = EMGNinaproTrack()
    recs = load_development(track, args.data_dir, args.subjects)

    rows = []
    for seed in SEEDS:
        cfg = {"preprocess": "none", "select": "none", "seed": seed}
        print(f"\nRunning baseline with cfg={cfg} ...", flush=True)
        res = track.evaluate_modes(recs, cfg=cfg)
        for mode in MODES:
            rep = res[mode]
            mean_f1 = rep["spread"]["macro_f1"]["mean"]
            print(f"  {mode}: pooled macro-F1 {rep['macro_f1']:.4f}, "
                  f"subject-mean macro-F1 {mean_f1:.4f}, kappa {rep['cohens_kappa']:.4f}")
            rows.append({"seed": seed, "mode": mode,
                         "pooled_macro_f1": round(float(rep["macro_f1"]), 4),
                         "subject_mean_macro_f1": round(float(mean_f1), 4),
                         "pooled_cohens_kappa": round(float(rep["cohens_kappa"]), 4)})

    print("\nSeed-to-seed variation of the unchanged baseline "
          f"({len(SEEDS)} seeds, same folds)")
    for mode in MODES:
        for key in ("pooled_macro_f1", "subject_mean_macro_f1"):
            v = np.array([r[key] for r in rows if r["mode"] == mode])
            print(f"  {mode:15s} {key:22s} mean {v.mean():.4f}  sd {v.std(ddof=1):.4f}  "
                  f"range {v.min():.4f}-{v.max():.4f}  (max-min {v.max() - v.min():.4f})")

    path = args.output_dir / "seed_noise_summary.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("Saved", path)


if __name__ == "__main__":
    sys.exit(main())
