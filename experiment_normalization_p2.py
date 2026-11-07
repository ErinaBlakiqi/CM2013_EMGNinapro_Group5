
"""Iteration 4, P2: Per-window global RMS normalization.

Ninapro DB1 E1, 10-channel EMG envelopes.

Uses one RMS scale per window, calculated across all
samples and channels. No statistics from other windows,
subjects, or future samples are used.

This script tests preprocessing correctness only.
No classifier or feature extraction is performed.
"""

import copy
import numpy as np

from emg_ninapro import EMGNinaproTrack


EPS = 1e-8


def normalize_global_rms(windows):
    """Normalize each EMG window using one RMS across all channels."""
    windows = np.asarray(windows, dtype=float)

    if windows.ndim != 3:
        raise ValueError("Expected a 3D EMG array.")

    # One RMS value for each window, across time and channels.
    rms = np.sqrt(
        np.mean(windows ** 2, axis=(1, 2), keepdims=True)
    )

    return windows / np.maximum(rms, EPS)


class P2NormalizedTrack(EMGNinaproTrack):
    """Apply P2 normalization in the preprocessing stage."""

    def preprocess(self, rec, cfg=None):
        processed = super().preprocess(rec, cfg)

        new_rec = copy.copy(processed)
        new_rec.epochs = dict(processed.epochs)
        new_rec.epochs["emg"] = normalize_global_rms(
            processed.epochs["emg"]
        )

        return new_rec


def main():
    track = EMGNinaproTrack()

    # Synthetic recordings only.
    recs = track.smoke(
        n_subjects=2,
        n_reps=2,
        win_per_rep=2,
    )
    track.assert_no_holdout(recs)

    original = np.asarray(recs[0].epochs["emg"])
    original_copy = original.copy()

    normalized = normalize_global_rms(original)

    # Test 1: Signal dimensions are preserved.
    assert normalized.shape == original.shape

    # Test 2: Active windows have global RMS approximately 1.
    original_rms = np.sqrt(
        np.mean(original ** 2, axis=(1, 2))
    )
    normalized_rms = np.sqrt(
        np.mean(normalized ** 2, axis=(1, 2))
    )

    active = original_rms >= EPS

    np.testing.assert_allclose(
        normalized_rms[active],
        np.ones(np.count_nonzero(active)),
        rtol=1e-6,
        atol=1e-6,
    )

    # Test 3: Zero-amplitude windows remain zero.
    zero_test = np.zeros((1, 20, 10))

    np.testing.assert_array_equal(
        normalize_global_rms(zero_test),
        zero_test,
    )

    # Test 4: Changing another window cannot affect this one.
    modified = original.copy()
    modified[1] *= 100

    np.testing.assert_allclose(
        normalize_global_rms(modified)[0],
        normalized[0],
    )

    # Test 5: Relative channel amplitudes are preserved.
    np.testing.assert_allclose(
        normalized[0, :, 0] / normalized[0, :, 1],
        original[0, :, 0] / original[0, :, 1],
        rtol=1e-6,
        atol=1e-6,
    )

    # Test 6: Original data are unchanged.
    np.testing.assert_array_equal(original, original_copy)

    # Test 7: Direct preprocessing integration.
    p2_track = P2NormalizedTrack()
    processed_rec = p2_track.preprocess(
        recs[0],
        cfg={"preprocess": "none"},
    )

    np.testing.assert_allclose(
        processed_rec.epochs["emg"],
        normalized,
    )

    np.testing.assert_array_equal(
        recs[0].epochs["emg"],
        original_copy,
    )

    print("P2 normalization correctness tests: PASSED")
    print("P2 preprocessing integration test: PASSED")
    print("Original shape:", original.shape)
    print("Normalized shape:", normalized.shape)
    print("No feature extraction or classifier evaluation performed.")


if __name__ == "__main__":
    main()
