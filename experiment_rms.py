import numpy as np
from emg_ninapro import EMGNinaproTrack


# Experiment model: remove RMS, keep everything else
class NoRMSTrack(EMGNinaproTrack):

    def extract_features(self, rec, cfg=None):
        X, y, group = super().extract_features(rec, cfg)

        # Each channel has:
        # [MAV, RMS, WL, VAR, MNF]
        # Remove positions 1, 6, 11, ... 46
        keep_cols = [
            i for i in range(X.shape[1])
            if i % 5 != 1
        ]

        return X[:, keep_cols], y, group


# Load the same real dataset for both experiments
baseline_track = EMGNinaproTrack()
experiment_track = NoRMSTrack()

recs = baseline_track.load("data/ninapro_db1")

if not recs:
    raise RuntimeError("No Ninapro recordings found. Check the data path.")

# Confirm the feature counts
X_baseline, _, _ = baseline_track.extract_features(recs[0])
X_no_rms, _, _ = experiment_track.extract_features(recs[0])

assert X_baseline.shape[1] == 50
assert X_no_rms.shape[1] == 40

print("Baseline features:", X_baseline.shape[1])
print("Without RMS:", X_no_rms.shape[1])

# Run both evaluations with the same recordings
baseline_results = baseline_track.evaluate_modes(recs)
experiment_results = experiment_track.evaluate_modes(recs)

for mode in ("within_subject", "new_subject"):
    print(f"\n{mode}")

    for name, results in [
        ("Baseline", baseline_results),
        ("Without RMS", experiment_results),
    ]:
        report = results[mode]

        print(
            name,
            "Macro-F1:", report["macro_f1"],
            "Kappa:", report["cohens_kappa"],
        )