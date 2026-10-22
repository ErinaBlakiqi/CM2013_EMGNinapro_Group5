
import numpy as np
from emg_ninapro import EMGNinaproTrack


class IQRTrack(EMGNinaproTrack):
    """Baseline features + IQR for each EMG channel."""

    def extract_features(self, rec, cfg=None):
        # Original baseline features: 50 columns
        X, y, group = super().extract_features(rec, cfg)

        # Original EMG windows: [windows, 20 samples, 10 channels]
        windows = rec.epochs["emg"]

        # Calculate IQR for each channel in each window
        q75 = np.percentile(windows, 75, axis=1)
        q25 = np.percentile(windows, 25, axis=1)
        iqr = q75 - q25

        # IQR shape: [windows, 10]
        # Append to the 50 baseline features
        X_with_iqr = np.hstack([X, iqr])

        return X_with_iqr, y, group


# Load the same real Ninapro data
baseline_track = EMGNinaproTrack()
iqr_track = IQRTrack()

recs = baseline_track.load("data/ninapro_db1")

if not recs:
    raise RuntimeError("No Ninapro recordings found.")

# Verify the feature counts
X_base, _, _ = baseline_track.extract_features(recs[0])
X_iqr, _, _ = iqr_track.extract_features(recs[0])

assert X_base.shape[1] == 50
assert X_iqr.shape[1] == 60

print("Baseline features:", X_base.shape[1])
print("Baseline + IQR features:", X_iqr.shape[1])

# Evaluate both models using the same recordings
baseline_results = baseline_track.evaluate_modes(recs)
iqr_results = iqr_track.evaluate_modes(recs)

# Compare the results
for mode in ("within_subject", "new_subject"):
    print(f"\n{mode}")

    for name, results in [
        ("Baseline", baseline_results),
        ("Baseline + IQR", iqr_results),
    ]:
        report = results[mode]

        print(
            name,
            "Macro-F1:", report["macro_f1"],
            "Kappa:", report["cohens_kappa"],
        )
