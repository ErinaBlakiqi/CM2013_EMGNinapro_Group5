#by erina


"""Iteration 4: EMG amplitude diagnostics on Ninapro DB1 S1-S10.

Investigates between-subject channel-amplitude differences before choosing
a normalization method. No classifier training or performance evaluation.
Official hold-out subjects S23-S27 are excluded.
"""

from pathlib import Path
import csv
import numpy as np

from emg_ninapro import EMGNinaproTrack


DATA_DIR = Path.home() / "cm2013_data" / "train"
CACHE_DIR = Path.home() / "cm2013_data" / "cache"
OUTPUT_DIR = Path.home() / "cm2013_data" / "experiment_results"
EXPECTED_SUBJECTS = {f"S{i}" for i in range(1, 11)}


def main():
    track = EMGNinaproTrack()

    # Verify file identities before loading development recordings.
    files = sorted(DATA_DIR.rglob("*_E1.mat"))
    found_subjects = [p.name.split("_")[0] for p in files]

    if (
        set(found_subjects) != EXPECTED_SUBJECTS
        or len(found_subjects) != 10
    ):
        raise ValueError(
            f"Expected exactly S1-S10 (one E1 file each), "
            f"found: {found_subjects}"
        )

    recs = track.load_cached(str(DATA_DIR), str(CACHE_DIR))
    track.assert_no_holdout(recs)

    if {r.group for r in recs} != EXPECTED_SUBJECTS or len(recs) != 10:
        raise ValueError("Loaded recordings do not match S1-S10.")

    rows = []

    for rec in sorted(recs, key=lambda r: int(r.group[1:])):
        windows = np.asarray(rec.epochs["emg"], dtype=float)

        if windows.ndim != 3 or windows.shape[2] != 10:
            raise ValueError(f"Unexpected EMG shape for {rec.group}")

        # DB1 contains rectified EMG envelopes.
        # Calculate the mean absolute amplitude for each channel.
        channel_means = np.mean(np.abs(windows), axis=(0, 1))

        row = {"subject": rec.group, "n_windows": len(windows)}
        row.update({
            f"CH{i + 1}_mean_abs": float(value)
            for i, value in enumerate(channel_means)
        })
        rows.append(row)

        print(
            f"{rec.group}: {len(windows)} windows | "
            f"channel amplitudes: {np.round(channel_means, 4)}"
        )

    # Descriptive comparison across subjects; not model evaluation.
    amplitude_matrix = np.array([
        [row[f"CH{i}_mean_abs"] for i in range(1, 11)]
        for row in rows
    ])

    print("\nAcross-subject channel amplitude summary:")
    for i in range(10):
        values = amplitude_matrix[:, i]
        print(
            f"CH{i + 1}: mean={values.mean():.4f}, "
            f"SD={values.std(ddof=1):.4f}, "
            f"min={values.min():.4f}, max={values.max():.4f}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "amplitude_diagnostics_S1_S10.csv"

    with output_file.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved diagnostic results to: {output_file}")


if __name__ == "__main__":
    main()
