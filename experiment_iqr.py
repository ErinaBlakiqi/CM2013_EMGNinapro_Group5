"""Compare the unchanged baseline against ten appended IQR features."""
import numpy as np
from emg_ninapro import EMGNinaproTrack
from experiment_common import (EXPERIMENT_CFG, arguments, load_development,
                               print_comparison)


class IQRTrack(EMGNinaproTrack):
    def extract_features(self, rec, cfg=None):
        X, y, group = super().extract_features(rec, cfg)
        if X.shape[1] != 50:
            raise ValueError("IQR comparison requires the original 50-feature baseline.")
        # Preserve all 50 baseline columns, then append IQR for CH1 through CH10.
        # rec has already passed through preprocess() when used by the harness.
        q25, q75 = np.percentile(rec.epochs["emg"], [25, 75], axis=1, method="linear")
        return np.hstack([X, q75 - q25]), y, group


def main(argv=None):
    args = arguments(__doc__, argv)
    baseline = EMGNinaproTrack()
    modified = IQRTrack()
    recs = load_development(baseline, args.data_dir)
    X_base, _, _ = baseline.extract_features(recs[0])
    X_modified, _, _ = modified.extract_features(recs[0])
    assert X_base.shape[1] == 50 and X_modified.shape[1] == 60
    np.testing.assert_array_equal(X_modified[:, :50], X_base)
    print_comparison([
        ("Baseline", baseline.evaluate_modes(recs, cfg=EXPERIMENT_CFG)),
        ("Baseline + IQR", modified.evaluate_modes(recs, cfg=EXPERIMENT_CFG)),
    ])


if __name__ == "__main__":
    main()
