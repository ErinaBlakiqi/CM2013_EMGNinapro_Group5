
"""
SVM classification experiment
Ninapro DB1 - Exercise E1

Development subjects: S1-S10
Final holdout: S23-S27
"""

from pathlib import Path

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from emg_ninapro import EMGNinaproTrack


DATA_DIR = Path("data/ninapro")
CACHE_DIR = Path.home() / "cm2013_data" / "cache"

EXPECTED_SUBJECTS = {f"S{i}" for i in range(1, 11)}


def create_svm_model():
    return make_pipeline(
        StandardScaler(),
        SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            class_weight="balanced",
        ),
    )


def main():
    track = EMGNinaproTrack()

    # Verify that only development subjects are present.
    files = sorted(DATA_DIR.rglob("*_E1.mat"))
    found_subjects = [p.name.split("_")[0] for p in files]

    if (
        set(found_subjects) != EXPECTED_SUBJECTS
        or len(found_subjects) != 10
    ):
        raise ValueError(
            f"Expected exactly S1-S10, found: {found_subjects}"
        )

    recs = track.load_cached(str(DATA_DIR), str(CACHE_DIR))
    track.assert_no_holdout(recs)

    if {r.group for r in recs} != EXPECTED_SUBJECTS or len(recs) != 10:
        raise ValueError("Loaded recordings do not match S1-S10.")

    cfg = {
        "preprocess": "none",
        "select": "none",
        "seed": 0,
    }

    X, y, subjects, repetitions = track._build(recs, cfg)

    print("=== SVM EXPERIMENT ===", flush=True)
    print("Subjects:", sorted(EXPECTED_SUBJECTS))
    print("Number of recordings:", len(recs))
    print("Feature matrix shape:", X.shape)

    model = create_svm_model()

    print("\n=== SVM PARAMETER CHECK ===")
    print(model)

    print("\n=== SVM LOSO EVALUATION ===", flush=True)

    report = track.evaluate(
        X,
        y,
        subjects,
        clf=model,
        cfg=cfg,
    )

    print(report["summary"], flush=True)

    print("\n=== PER-SUBJECT RESULTS ===")
    for row in sorted(
        report["per_group"],
        key=lambda r: int(r["group"][1:]),
    ):
        print(
            f'{row["group"]}: '
            f'{row["macro_f1"]:.3f}'
        )


if __name__ == "__main__":
    main()
