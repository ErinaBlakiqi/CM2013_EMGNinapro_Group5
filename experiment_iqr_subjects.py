
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import f1_score, cohen_kappa_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.base import clone

from emg_ninapro import EMGNinaproTrack
from experiment_iqr import IQRTrack


def evaluate_per_subject(track, recs):
    # Build the feature matrix and subject labels
    X, y, subjects, repetitions = track._build(recs)

    logo = LeaveOneGroupOut()
    results = []

    for train_idx, test_idx in logo.split(X, y, subjects):
        subject = subjects[test_idx][0]

        # Feature selection must use training data only
        selector = track.select_features(
            X[train_idx], y[train_idx], cfg=None
        )

        X_train = selector.transform(X[train_idx])
        X_test = selector.transform(X[test_idx])

        # Use the existing Random Forest baseline
        model = clone(track.baseline())
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


# Load the same real Ninapro data
baseline_track = EMGNinaproTrack()
iqr_track = IQRTrack()

recs = baseline_track.load("data/ninapro_db1")

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
comparison.to_csv("iqr_per_subject_results.csv", index=False)

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

plt.savefig("iqr_per_subject.png", dpi=150)

print("\nSaved results and plot.")
