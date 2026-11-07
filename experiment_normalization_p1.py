import copy

"""Iteration 4, P1: Per-window, per-channel RMS normalization.

Ninapro DB1 E1, development subjects S1-S10.

Each channel is normalized using only samples from its own
200 ms window. No subject-wide or cohort-wide statistics are fitted.

This script tests mathematical correctness only.
It does NOT evaluate classification performance.
"""

import numpy as np

from emg_ninapro import EMGNinaproTrack


EPS = 1e-8


def normalize_per_channel(windows):
    """Normalize each channel independently within each EMG window.

    Input shape: (n_windows, n_samples, n_channels).
    """
    windows = np.asarray(windows, dtype=float)

    if windows.ndim != 3:
        raise ValueError("Expected a 3D EMG window array.")

    # RMS over the time axis, independently for every window/channel.
    rms = np.sqrt(np.mean(windows ** 2, axis=1, keepdims=True))

    # Avoid division by zero for inactive channels.
    return windows / np.maximum(rms, EPS)


class P1NormalizedTrack(EMGNinaproTrack):
    """Apply per-window, per-channel RMS normalization before feature extraction."""

    def preprocess(self, rec, cfg=None):
        # Preserve the existing preprocessing configuration.
        processed = super().preprocess(rec, cfg)

        new_rec = copy.copy(processed)
        new_rec.epochs = dict(processed.epochs)
        new_rec.epochs["emg"] = normalize_per_channel(
            processed.epochs["emg"]
        )

        return new_rec


def main():
    track = EMGNinaproTrack()

    # Synthetic data only: no real subjects or hold-out data.
    recs = track.smoke(n_subjects=2, n_reps=2, win_per_rep=2)
    track.assert_no_holdout(recs)

    original = np.asarray(recs[0].epochs["emg"])
    original_copy = original.copy()

    normalized = normalize_per_channel(original)

    assert normalized.shape == original.shape
    np.testing.assert_array_equal(original, original_copy)

    # Each nonzero channel/window should have RMS approximately 1.
    original_rms = np.sqrt(np.mean(original ** 2, axis=1))
    normalized_rms = np.sqrt(np.mean(normalized ** 2, axis=1))

    active = original_rms >= EPS
    np.testing.assert_allclose(
        normalized_rms[active],
        np.ones(np.count_nonzero(active)),
        rtol=1e-6,
        atol=1e-6,
    )

    # A zero-amplitude channel must remain zero.
    zero_test = np.zeros((1, 20, 10))
    np.testing.assert_array_equal(
        normalize_per_channel(zero_test),
        zero_test,
    )

    # Verify that changing another window does not change this one.
    modified = original.copy()
    modified[1] *= 100
    np.testing.assert_allclose(
        normalize_per_channel(modified)[0],
        normalized[0],
    )

        # Verify that the track's preprocessing pipeline applies P1.
    p1_track = P1NormalizedTrack()
    processed_rec = p1_track.preprocess(recs[0], cfg={"preprocess": "none"})

    np.testing.assert_allclose(
        processed_rec.epochs["emg"],
        normalize_per_channel(original),
    )

    np.testing.assert_array_equal(
        recs[0].epochs["emg"],
        original_copy,
    )

    print("P1 pipeline integration test: PASSED")

    print("P1 normalization correctness tests: PASSED")
    print("Original shape:", original.shape)
    print("Normalized shape:", normalized.shape)
    print("No classifier evaluation performed.")
    


if __name__ == "__main__":
    main()
