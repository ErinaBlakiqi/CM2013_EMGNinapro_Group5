
"""Real-data preprocessing validation for P1 and P2.

Uses development subjects S1–S10 only.
No feature extraction or classification.
"""

import numpy as np

from emg_ninapro import EMGNinaproTrack
from experiment_normalization_p1 import normalize_per_channel
from experiment_normalization_p2 import normalize_global_rms


def main():
    track = EMGNinaproTrack()

    # Load the existing development recordings.
    recs = track.load_cached(
    data_dir="/Users/erinablakiqi/cm2013_data/train",
    cache_dir="/Users/erinablakiqi/cm2013_data/cache",
    exercise="E1",
    )

    # Enforce the official holdout restriction.
    track.assert_no_holdout(recs)

    subjects = sorted({int(r.group[1:]) for r in recs})
    assert subjects == list(range(1, 11)), (
        f"Unexpected subjects: {subjects}"
    )

    print("Loaded development subjects:", subjects)
    print("Number of recordings:", len(recs))
    print("No holdout subjects accessed.")

        # Validate P1 on real development recordings.
    total_windows = 0

    for rec in recs:
        original = np.asarray(rec.epochs["emg"])
        original_copy = original.copy()

        normalized = normalize_per_channel(original)

        # Check dimensions, numerical stability, and immutability.
        assert normalized.shape == original.shape
        assert np.all(np.isfinite(normalized))
        np.testing.assert_array_equal(original, original_copy)

        # Active channels should have unit RMS.
        original_rms = np.sqrt(
            np.mean(original ** 2, axis=1)
        )
        normalized_rms = np.sqrt(
            np.mean(normalized ** 2, axis=1)
        )

        active = original_rms >= 1e-8

        np.testing.assert_allclose(
            normalized_rms[active],
            1.0,
            rtol=1e-6,
            atol=1e-6,
        )

        total_windows += len(original)
        print(f"{rec.group}: P1 validation PASSED ({len(original)} windows)")

    print(f"P1 real-data validation PASSED: {total_windows} windows")

        # Validate P2 on real development recordings.
    total_p2_windows = 0

    for rec in recs:
        original = np.asarray(rec.epochs["emg"])
        original_copy = original.copy()

        normalized = normalize_global_rms(original)

        # Check dimensions, numerical stability, and immutability.
        assert normalized.shape == original.shape
        assert np.all(np.isfinite(normalized))
        np.testing.assert_array_equal(original, original_copy)

        # Active windows should have global RMS equal to 1.
        original_rms = np.sqrt(
            np.mean(original ** 2, axis=(1, 2))
        )
        normalized_rms = np.sqrt(
            np.mean(normalized ** 2, axis=(1, 2))
        )

        active = original_rms >= 1e-8

        np.testing.assert_allclose(
            normalized_rms[active],
            1.0,
            rtol=1e-6,
            atol=1e-6,
        )

        total_p2_windows += len(original)

        print(
            f"{rec.group}: P2 validation PASSED "
            f"({len(original)} windows)"
        )

    print(
        f"P2 real-data validation PASSED: "
        f"{total_p2_windows} windows"
    )

        # Compare channel RMS patterns for one real EMG window.
    rec = next(r for r in recs if r.group == "S1")

    original = np.asarray(rec.epochs["emg"])

    # Choose the window with the largest global RMS to avoid
    # illustrating an almost-silent window.
    global_rms = np.sqrt(np.mean(original ** 2, axis=(1, 2)))
    window_idx = int(np.argmax(global_rms))

    window = original[window_idx:window_idx + 1]

    p1 = normalize_per_channel(window)
    p2 = normalize_global_rms(window)

    for name, signal in [
        ("Original", window),
        ("P1", p1),
        ("P2", p2),
    ]:
        channel_rms = np.sqrt(np.mean(signal ** 2, axis=1))[0]
        print(f"{name} channel RMS:", np.round(channel_rms, 4))

    print("Illustrative S1 window index:", window_idx)


if __name__ == "__main__":
    main()
