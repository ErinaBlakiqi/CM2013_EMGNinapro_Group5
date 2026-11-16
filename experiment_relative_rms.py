"""Compare regular RMS and relative RMS on the S1-S10 development cohort."""

import numpy as np

from emg_ninapro import EMGNinaproTrack
from experiment_common import (
    EXPERIMENT_CFG,
    arguments,
    load_development,
    print_comparison,
)


class RelativeRMSTrack(EMGNinaproTrack):
    def extract_features(self, rec, cfg=None):
        features, labels, group = super().extract_features(rec, cfg)
        if features.shape[1] != 50:
            raise ValueError("Relative RMS requires the original 50-feature ordering.")

        relative_features = features.copy()
        rms = features[:, 1::5]
        total_rms = rms.sum(axis=1, keepdims=True)
        relative_features[:, 1::5] = np.divide(
            rms, total_rms, out=np.zeros_like(rms), where=total_rms != 0
        )
        return relative_features, labels, group


def main(argv=None):
    args = arguments(__doc__, argv)
    if args.subjects != 10:
        raise SystemExit("Use --subjects 10 for this comparison.")

    baseline = EMGNinaproTrack()
    relative = RelativeRMSTrack()
    records = load_development(baseline, args.data_dir, args.subjects)

    features, _, _ = relative.extract_features(records[0], EXPERIMENT_CFG)
    if features.ndim != 2 or features.shape[1] != 50:
        raise ValueError("Relative RMS must return 50 features per window.")

    results = [
        ("Baseline", baseline.evaluate_modes(records, cfg=EXPERIMENT_CFG)),
        ("Relative RMS", relative.evaluate_modes(records, cfg=EXPERIMENT_CFG)),
    ]
    print_comparison(results)


if __name__ == "__main__":
    main()