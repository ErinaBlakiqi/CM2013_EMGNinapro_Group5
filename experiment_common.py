"""Shared settings and development-data checks for the feature experiments."""
import argparse
from pathlib import Path
import re

DEVELOPMENT_SUBJECTS = {f"S{i}" for i in range(1, 6)}
EXPERIMENT_CFG = {"preprocess": "none", "select": "none", "seed": 0}


def arguments(description, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--data-dir", type=Path,
                        default=Path.home() / "cm2013_data" / "train")
    parser.add_argument("--output-dir", type=Path,
                        default=Path.home() / "cm2013_data" / "experiment_results")
    return parser.parse_args(argv)


def load_development(track, data_dir):
    """Require exactly S1-S5 and reject other subjects BEFORE loading .mat data.

    Ordinary loading is intentional until cache equality has been verified.
    """
    files = sorted(data_dir.rglob("*_E1.mat"))
    if not files:
        raise FileNotFoundError(f"No E1 recordings found in {data_dir}")
    subjects = []
    for path in files:
        match = re.match(r"S(\d+)_", path.name)
        if match is None:
            raise ValueError(f"Unrecognized recording name: {path.name}")
        subjects.append(f"S{int(match.group(1))}")
    if set(subjects) != DEVELOPMENT_SUBJECTS or len(subjects) != 5:
        raise ValueError("Expected exactly one E1 recording for each of S1-S5; "
                         f"found {subjects}. Use a separate development folder.")
    recs = track.load(str(data_dir))
    track.assert_no_holdout(recs)
    if {r.group for r in recs} != DEVELOPMENT_SUBJECTS or len(recs) != 5:
        raise ValueError("Loaded recordings do not match the required S1-S5 subset.")
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
