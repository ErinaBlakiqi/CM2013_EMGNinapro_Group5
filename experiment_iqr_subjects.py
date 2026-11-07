
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import f1_score, cohen_kappa_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.base import clone

from emg_ninapro import EMGNinaproTrack
from experiment_iqr import IQRTrack
from experiment_common import EXPERIMENT_CFG, arguments, load_development


def evaluate_per_subject(track, recs, cfg=None):
    cfg = dict(EXPERIMENT_CFG if cfg is None else cfg)
    track.assert_no_holdout(recs)
    # Build the feature matrix and subject labels
    X, y, subjects, repetitions = track._build(recs, cfg=cfg)

    logo = LeaveOneGroupOut()
    results = []

    for train_idx, test_idx in logo.split(X, y, subjects):
        subject = subjects[test_idx][0]

        # Feature selection must use training data only
        selector = track.select_features(
            X[train_idx], y[train_idx], cfg=cfg
        )

        X_train = selector.transform(X[train_idx])
        X_test = selector.transform(X[test_idx])

        # Use the existing Random Forest baseline
        model = clone(track.baseline(cfg=cfg))
        model.fit(X_train, y[train_idx])

        predictions = model.predict(X_test)

        results.append({
            "Subject": subject,
            "Macro-F1": f1_score(
                y[test_idx],
                predictions,
                average="macro",
                zero_division=0
            ),
            "Kappa": cohen_kappa_score(
                y[test_idx], predictions
            )
        })

    return pd.DataFrame(results)


def main(argv=None):
    args = arguments("Per-subject IQR comparison on S1-S5", argv)
    # Load the same real Ninapro data
    baseline_track = EMGNinaproTrack()
    iqr_track = IQRTrack()

    recs = load_development(baseline_track, args.data_dir)

    if not recs:
        raise RuntimeError("No recordings found.")

    # Evaluate both feature sets
    baseline_df = evaluate_per_subject(baseline_track, recs)
    iqr_df = evaluate_per_subject(iqr_track, recs)

    # Combine results
    comparison = baseline_df.merge(
        iqr_df,
        on="Subject",
        suffixes=("_Baseline", "_IQR")
    )

    comparison["F1_Change"] = (
        comparison["Macro-F1_IQR"]
        - comparison["Macro-F1_Baseline"]
    )

    comparison["Kappa_Change"] = (
        comparison["Kappa_IQR"]
        - comparison["Kappa_Baseline"]
    )

    comparison = comparison.sort_values("Subject")

    print("\nPer-subject comparison:")
    print(comparison.round(3).to_string(index=False))

    print("\nSubjects improved:",
          (comparison["F1_Change"] > 0).sum())

    print("Subjects worsened:",
          (comparison["F1_Change"] < 0).sum())

    print("Mean per-subject F1 change:",
          comparison["F1_Change"].mean().round(4))

    # Save results
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(args.output_dir / "iqr_per_subject_results.csv", index=False)

    print("\nMean and SD across subjects:")
    print(comparison.select_dtypes(include="number").agg(["mean", "std"]))

    # Plot per-subject differences
    plt.figure(figsize=(8, 4))

    plt.bar(
        comparison["Subject"],
        comparison["F1_Change"]
    )

    plt.axhline(0, color="black", linewidth=1)
    plt.ylabel("Change in Macro-F1")
    plt.xlabel("Held-out Subject")
    plt.title("IQR Effect on New-Subject Classification")
    plt.tight_layout()

    plt.savefig(args.output_dir / "iqr_per_subject.png", dpi=150)
    plt.close()

    print("\nSaved results and plot to", args.output_dir)


if __name__ == "__main__":
    main()
