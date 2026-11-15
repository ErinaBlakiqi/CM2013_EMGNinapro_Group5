"""Shared settings and development-data checks for the feature experiments."""
import argparse
from pathlib import Path
import re

DEVELOPMENT_SUBJECTS = {f"S{i}" for i in range(1, 6)}
EXPERIMENT_CFG = {"preprocess": "none", "select": "none", "seed": 0}


def arguments(description, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--subjects", type=int, choices=(5, 10), default=5,
                        help="Development cohort: S1-S5 or S1-S10 (default: 5).")
    parser.add_argument("--data-dir", type=Path,
                        help="E1 folder; defaults to train for 5 subjects, train_s1_s10 for 10.")
    parser.add_argument("--output-dir", type=Path,
                        help="Output folder; defaults to experiment_results/s1_s5 or s1_s10.")
    args = parser.parse_args(argv)
    root = Path.home() / "cm2013_data"
    if args.data_dir is None:
        args.data_dir = root / ("train" if args.subjects == 5 else "train_s1_s10")
    if args.output_dir is None:
        args.output_dir = root / "experiment_results" / f"s1_s{args.subjects}"
    return args


def load_development(track, data_dir, subject_count=5):
    """Check the selected cohort before reading any recording data."""
    if subject_count not in (5, 10):
        raise ValueError("Choose 5 or 10 development subjects.")
    expected_subjects = {f"S{i}" for i in range(1, subject_count + 1)}
    cohort = f"S1-S{subject_count}"
    files = sorted(data_dir.rglob("*_E1.mat"))
    if not files:
        raise FileNotFoundError(f"No E1 recordings found in {data_dir}")
    subjects = []
    for path in files:
        match = re.match(r"S(\d+)_", path.name)
        if match is None:
            raise ValueError(f"Unrecognized recording name: {path.name}")
        subjects.append(f"S{int(match.group(1))}")
    if set(subjects) != expected_subjects or len(subjects) != subject_count:
        raise ValueError(f"Expected exactly one E1 recording for each of {cohort}; "
                         f"found {subjects}. Use a separate development folder.")
    recs = track.load(str(data_dir))
    track.assert_no_holdout(recs)
    if {r.group for r in recs} != expected_subjects or len(recs) != subject_count:
        raise ValueError(f"Loaded recordings do not match the required {cohort} subset.")
    print("Development subjects:", sorted(expected_subjects, key=lambda g: int(g[1:])))
    print("Windows:", sum(len(r.labels) for r in recs))
    return recs


def print_comparison(results):
    print("Configuration:", EXPERIMENT_CFG)
    for mode in ("within_subject", "new_subject"):
        print(f"\n{mode}")
        for name, modes in results:
            report = modes[mode]
            print(name, "pooled Macro-F1:", report["macro_f1"],
                  "pooled kappa:", report["cohens_kappa"])
            print("  Per-subject summary:", report["summary"])
