"""Compare the unchanged baseline against removal of one RMS per channel."""
import numpy as np
from emg_ninapro import EMGNinaproTrack
from experiment_common import (EXPERIMENT_CFG, arguments, load_development,
                               print_comparison)


class NoRMSTrack(EMGNinaproTrack):
    def extract_features(self, rec, cfg=None):
        X, y, group = super().extract_features(rec, cfg)
        if X.shape[1] != 50:
            raise ValueError("RMS ablation requires the original 50-feature ordering.")
        keep_cols = [i for i in range(50) if i % 5 != 1]
        return X[:, keep_cols], y, group


def main(argv=None):
    args = arguments(__doc__, argv)
    baseline = EMGNinaproTrack()
    modified = NoRMSTrack()
    recs = load_development(baseline, args.data_dir)
    X_base, _, _ = baseline.extract_features(recs[0])
    X_modified, _, _ = modified.extract_features(recs[0])
    assert X_base.shape[1] == 50 and X_modified.shape[1] == 40
    np.testing.assert_array_equal(X_modified, np.delete(X_base, np.arange(1, 50, 5), axis=1))
    print_comparison([
        ("Baseline", baseline.evaluate_modes(recs, cfg=EXPERIMENT_CFG)),
        ("Without RMS", modified.evaluate_modes(recs, cfg=EXPERIMENT_CFG)),
    ])


if __name__ == "__main__":
    main()
