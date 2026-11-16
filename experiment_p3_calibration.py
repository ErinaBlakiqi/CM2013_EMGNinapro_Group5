"""Iteration 5 - P3 per-subject calibration vs the identity baseline.

P3 (`preprocess="subject_calibration"`) divides each channel of a subject by
that channel's RMS over the subject's calibration repetition (repetition 1 of
every gesture). See EMGNinaproTrack.preprocess().

Fair comparison: the calibration repetition is used to compute the scale, so
its windows are REMOVED from training and scoring for BOTH configurations.
Baseline and P3 are therefore trained and scored on the same windows (reps 2-10)
and the same folds; only `preprocess` differs. Because the window set differs
from earlier iterations, this run reports its own baseline - compare P3 only
with that baseline.

The script first runs correctness tests on synthetic data; the evaluation only starts if
they all pass.

Outputs (in --output-dir):
  p3_eval_summary.csv, p3_eval_per_subject.csv
"""
import csv
import sys

import numpy as np

from adapter import Recording
from emg_ninapro import EMGNinaproTrack
from experiment_common import arguments, load_development

CONFIGS = [("Baseline (identity), reps 2-10", "none"),
           ("P3 subject calibration, reps 2-10", "subject_calibration")]
MODES = ("within_subject", "new_subject")
METRICS = ("macro_f1", "cohens_kappa", "balanced_accuracy", "accuracy")


def split_calibration(rec):
    """Evaluation setup: remove the calibration repetition (the lowest repetition
    number) from the windows that are trained on and scored, and keep its windows
    in meta["calibration_emg"] so P3 can compute the scale from them. Applied to
    every recording, for BOTH configurations, so baseline and P3 are trained and
    scored on identical windows. Not used for inference/predictions.csv."""
    reps = np.asarray(rec.meta["rep"])
    calib_rep = int(reps.min())
    keep = reps != calib_rep
    emg = np.asarray(rec.epochs["emg"])
    meta = dict(rec.meta)
    meta["rep"] = reps[keep]
    meta["calibration_emg"] = emg[~keep]
    meta["calibration_rep"] = calib_rep
    return Recording(group=rec.group, fs=rec.fs, epochs={"emg": emg[keep]},
                     labels=np.asarray(rec.labels)[keep], meta=meta)


# ----------------------------------------------------------------- tests
def _synthetic(seed=0, gain=None):
    rng = np.random.default_rng(seed)
    n_rep, per_rep = 4, 6
    reps = np.repeat(np.arange(1, n_rep + 1), per_rep)
    wins = np.abs(rng.normal(size=(len(reps), 20, 10)))
    if gain is not None:
        wins = wins * gain[None, None, :]
    labels = np.array([f"g{(i % 3) + 1:02d}" for i in range(len(reps))])
    return Recording(group="S1", fs=100.0, epochs={"emg": wins}, labels=labels,
                     meta={"rep": reps})


def run_tests():
    track = EMGNinaproTrack()
    cfg = {"preprocess": "subject_calibration"}

    # 1. shape preserved, finite output, original recording unchanged
    rec = _synthetic()
    before = rec.epochs["emg"].copy()
    out = track.preprocess(rec, cfg)
    assert out.epochs["emg"].shape == before.shape
    assert np.isfinite(out.epochs["emg"]).all()
    np.testing.assert_array_equal(rec.epochs["emg"], before)
    np.testing.assert_array_equal(out.labels, rec.labels)

    # 2. calibration repetition has unit RMS per channel after scaling
    cal = out.epochs["emg"][out.meta["rep"] == 1]
    np.testing.assert_allclose(np.sqrt(np.mean(cal ** 2, axis=(0, 1))), 1.0, rtol=1e-10)

    # 3. scale uses ONLY the calibration repetition: changing reps 2+ changes nothing in the scale
    rec2 = _synthetic()
    rec2.epochs["emg"][rec2.meta["rep"] > 1] *= 50.0
    out2 = track.preprocess(rec2, cfg)
    np.testing.assert_allclose(out2.meta["calibration_scale"], out.meta["calibration_scale"])

    # 4. removes a per-subject channel gain (the problem found in the diagnostics)
    gain = np.array([0.003, 0.1, 1, 5, 0.5, 2, 10, 0.02, 1, 3])
    out_g = track.preprocess(_synthetic(gain=gain), cfg)
    np.testing.assert_allclose(out_g.epochs["emg"], out.epochs["emg"], rtol=1e-10)

    # 5. keeps amplitude differences between repetitions/gestures within a subject
    rec3 = _synthetic()
    rec3.epochs["emg"][rec3.meta["rep"] == 3] *= 4.0
    out3 = track.preprocess(rec3, cfg)
    r2 = np.sqrt(np.mean(out3.epochs["emg"][out3.meta["rep"] == 2] ** 2))
    r3 = np.sqrt(np.mean(out3.epochs["emg"][out3.meta["rep"] == 3] ** 2))
    assert r3 > 3 * r2

    # 6. a silent channel stays zero (no division by zero)
    rec4 = _synthetic()
    rec4.epochs["emg"][:, :, 4] = 0.0
    out4 = track.preprocess(rec4, cfg)
    assert np.isfinite(out4.epochs["emg"]).all() and (out4.epochs["emg"][:, :, 4] == 0).all()

    # 7. evaluation split: calibration rep removed, and P3 gives the SAME scale
    #    whether the calibration windows are inside the recording or kept aside
    full = _synthetic()
    ev = split_calibration(full)
    assert 1 not in set(ev.meta["rep"].tolist())
    assert len(ev.labels) == ev.epochs["emg"].shape[0] == len(ev.meta["rep"]) == 18
    np.testing.assert_allclose(track.preprocess(ev, cfg).meta["calibration_scale"],
                               track.preprocess(full, cfg).meta["calibration_scale"])
    np.testing.assert_allclose(track.preprocess(ev, cfg).epochs["emg"],
                               track.preprocess(full, cfg).epochs["emg"][full.meta["rep"] > 1])

    # 8. other preprocess options are unaffected
    np.testing.assert_array_equal(track.preprocess(_synthetic(), {"preprocess": "none"}).epochs["emg"],
                                  _synthetic().epochs["emg"])
    print("P3 correctness tests: 8/8 PASSED")


# ------------------------------------------------------------ evaluation
def per_subject_f1(report):
    return {row["group"]: float(row["macro_f1"]) for row in report["per_group"]}


def main(argv=None):
    args = arguments(__doc__, argv)
    run_tests()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    track = EMGNinaproTrack()
    recs = [split_calibration(r) for r in load_development(track, args.data_dir, args.subjects)]
    print("Windows used for training/scoring (calibration repetition removed):",
          sum(len(r.labels) for r in recs),
          "| calibration windows set aside:", sum(len(r.meta["calibration_emg"]) for r in recs))

    # Per-subject calibration scales (evidence of between-subject amplitude differences)
    scales = np.array([track.preprocess(r, {"preprocess": "subject_calibration"})
                       .meta["calibration_scale"] for r in recs])
    print("Calibration scale per channel, across subjects: min",
          np.round(scales.min(0), 4), "\n                                                max",
          np.round(scales.max(0), 4))

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

    base_name = CONFIGS[0][0]
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

    print("\nPaired per-subject change in macro-F1, P3 vs baseline (same windows, same folds)")
    for mode in MODES:
        d = np.array([r["change_vs_baseline"] for r in subject_rows
                      if r["config"] == CONFIGS[1][0] and r["mode"] == mode])
        sd = d.std(ddof=1)
        se = sd / np.sqrt(len(d))
        ratio = f"{d.mean() / se:+.2f}" if se > 0 else "n/a (identical scores)"
        print(f"  {mode:15s} mean {d.mean():+.4f} (sd {sd:.4f}, SE {se:.4f}, "
              f"mean/SE {ratio}); improved {int((d > 0).sum())}/{len(d)}, "
              f"worse {int((d < 0).sum())}/{len(d)}")
    for mode in MODES:
        print(f"  {mode} per subject:",
              {r["subject"]: r["change_vs_baseline"] for r in subject_rows
               if r["config"] == CONFIGS[1][0] and r["mode"] == mode})

    for fname, rows in (("p3_eval_summary.csv", summary_rows),
                        ("p3_eval_per_subject.csv", subject_rows)):
        path = args.output_dir / fname
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print("Saved", path)


if __name__ == "__main__":
    sys.exit(main())
