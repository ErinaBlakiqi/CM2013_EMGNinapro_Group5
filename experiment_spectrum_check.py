"""Spectrum check: is there noise in the Ninapro DB1 envelope that needs filtering?

Not a configuration comparison - nothing is selected from it. It computes a
Welch power spectral density (PSD) of the continuous 10-channel EMG of each
development subject (E1, whole recording), and reports:
  * the spectrum per channel (median across subjects), plotted on a log scale,
  * how much power lies at low frequencies (where the envelope's movement
    information is) versus high frequencies,
  * whether there is a narrow peak near 50 Hz (powerline) - at fs = 100 Hz,
    50 Hz is the Nyquist frequency, the highest frequency that can be represented.

Outputs (in --output-dir): spectrum_check.png, spectrum_check.csv
"""
import csv
import re
import sys

import numpy as np
from scipy.io import loadmat
from scipy.signal import welch

from emg_ninapro import FS, HOLDOUT_SUBJECTS
from experiment_common import arguments

NPERSEG = 256          # 2.56 s segments -> 0.39 Hz resolution
BANDS = [(0, 2), (2, 5), (5, 10), (10, 25), (25, 45), (45, 50)]


def main(argv=None):
    args = arguments(__doc__, argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    expected = {f"S{i}" for i in range(1, args.subjects + 1)}

    def subject_number(path):
        return int(re.match(r"S(\d+)_", path.name).group(1))

    files = sorted(args.data_dir.rglob("*_E1.mat"), key=subject_number)
    subjects = ["S" + str(subject_number(p)) for p in files]
    if set(subjects) != expected or len(subjects) != len(expected):
        raise ValueError(f"Expected one E1 file for each of {sorted(expected)}, found {subjects}")
    if any(int(s[1:]) in HOLDOUT_SUBJECTS for s in subjects):
        raise ValueError("Hold-out subject found in development folder.")
    print("Development subjects:", subjects)

    psds = []                                           # [subject, freq, channel]
    for p in files:
        emg = np.asarray(loadmat(p)["emg"], float)      # [N, 10] continuous envelope
        f, pxx = welch(emg, fs=FS, nperseg=NPERSEG, axis=0, detrend="constant")
        psds.append(pxx)
    psds = np.array(psds)
    med = np.median(psds, axis=0)                       # [freq, channel]

    # Power fraction per band (per subject & channel, then median)
    total = psds.sum(axis=1)
    rows = []
    print("\nShare of total power per band (median over subjects and channels):")
    for lo, hi in BANDS:
        m = (f >= lo) & (f < hi) if hi < 50 else (f >= lo) & (f <= hi)
        share = psds[:, m, :].sum(axis=1) / total
        print(f"  {lo:>2}-{hi:<2} Hz: {np.median(share) * 100:7.3f} %  "
              f"(max over subjects/channels {share.max() * 100:.3f} %)")
        rows.append({"band_hz": f"{lo}-{hi}", "median_share_pct": round(float(np.median(share) * 100), 4),
                     "max_share_pct": round(float(share.max() * 100), 4)})

    # Narrow-peak test near 50 Hz: PSD at the top bins vs the median of 40-48 Hz
    top = f >= 49
    ref = (f >= 40) & (f < 48)
    ratio = psds[:, top, :].max(axis=1) / np.median(psds[:, ref, :], axis=1)
    print(f"\nPeak test near 50 Hz: max PSD in 49-50 Hz / median PSD in 40-48 Hz = "
          f"median {np.median(ratio):.2f}, max {ratio.max():.2f} (over subjects and channels)")
    print("  (a powerline peak would give a ratio far above 1, e.g. >10)")
    rows.append({"band_hz": "peak_ratio_49-50_vs_40-48", "median_share_pct": round(float(np.median(ratio)), 3),
                 "max_share_pct": round(float(ratio.max()), 3)})

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for ch in range(med.shape[1]):
        ax.semilogy(f, med[:, ch], lw=1, label=f"CH{ch + 1}")
    ax.axvline(50, color="k", ls="--", lw=0.8)
    ax.text(49.5, ax.get_ylim()[1], "50 Hz = Nyquist\n(powerline)", ha="right", va="top", fontsize=8)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD (median across subjects)")
    ax.set_title(f"Ninapro DB1 E1 envelope, Welch PSD, {len(files)} development subjects")
    ax.legend(ncol=5, fontsize=7)
    ax.set_xlim(0, 50)
    fig.tight_layout()
    png = args.output_dir / "spectrum_check.png"
    fig.savefig(png, dpi=150)
    print("\nSaved", png)

    path = args.output_dir / "spectrum_check.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("Saved", path)


if __name__ == "__main__":
    sys.exit(main())
