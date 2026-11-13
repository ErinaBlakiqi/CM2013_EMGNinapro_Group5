"""
Random Forest tuning experiments
Ninapro DB1 - Exercise E1

Development subjects: S1-S10
Final holdout: S23-S27
"""

from pathlib import Path
from emg_ninapro import EMGNinaproTrack
from adapter import default_baseline


DATA_DIR = Path("data/ninapro")
CACHE_DIR = Path.home() / "cm2013_data" / "cache"

EXPECTED_SUBJECTS = {f"S{i}" for i in range(1, 11)}


def create_rf_model(max_features):
    # Create the existing Random Forest baseline.
    model = default_baseline(seed=0, imbalance="balanced")

    # Keep leaf size and tree depth fixed.
    # Change only max_features.
    model.set_params(
        clf__min_samples_leaf=10,
        clf__max_depth=10,
        clf__max_features=max_features,
    )

    return model



def evaluate_rf_models(track, recs):
    """
    Experiment 4: Compare Random Forest max_features values
    using Leave-One-Subject-Out evaluation.
    """
    cfg = {
        "preprocess": "none",
        "select": "none",
        "seed": 0,
    }

    X, y, subjects, repetitions = track._build(recs, cfg)

    feature_values = ["sqrt", "log2", 0.5, 1.0]
    subject_results = {}

    print("\n=== EXPERIMENT 4: MAX_FEATURES ===")

    for value in feature_values:
        print(f"\nEvaluating max_features={value}...", flush=True)

        model = create_rf_model(value)

        report = track.evaluate(
            X,
            y,
            subjects,
            clf=model,
            cfg=cfg,
        )

        print(report["summary"], flush=True)

        subject_results[value] = {
            row["group"]: row["macro_f1"]
            for row in report["per_group"]
        }

    print("\n=== PER-SUBJECT COMPARISON ===")
    print("Subject | sqrt | log2 | 0.5 | 1.0")

    for subject in sorted(
        subject_results["sqrt"],
        key=lambda s: int(s[1:]),
    ):
        scores = [
            subject_results[value][subject]
            for value in feature_values
        ]

        print(
            f"{subject:7} | "
            + " | ".join(f"{score:.3f}" for score in scores)
        )

    print("\n=== CHANGE COMPARED WITH MAX_FEATURES='sqrt' ===")

    for value in ["log2", 0.5, 1.0]:
        differences = [
            subject_results[value][subject]
            - subject_results["sqrt"][subject]
            for subject in subject_results["sqrt"]
        ]

        improved = sum(d > 0 for d in differences)
        worsened = sum(d < 0 for d in differences)
        unchanged = sum(d == 0 for d in differences)

        print(
            f"max_features={value}: "
            f"improved={improved}, "
            f"worsened={worsened}, "
            f"unchanged={unchanged}, "
            f"mean difference={sum(differences) / len(differences):+.4f}"
        )




def main():
    track = EMGNinaproTrack()

    # Check which subjects exist before loading data.
    files = sorted(DATA_DIR.rglob("*_E1.mat"))
    found_subjects = [p.name.split("_")[0] for p in files]

    if (
        set(found_subjects) != EXPECTED_SUBJECTS
        or len(found_subjects) != 10
    ):
        raise ValueError(
            f"Expected exactly S1-S10, found: {found_subjects}"
        )

    # Load the same development data as the other experiments.
    recs = track.load_cached(str(DATA_DIR), str(CACHE_DIR))

    # Make sure the final holdout is excluded.
    track.assert_no_holdout(recs)

    if {r.group for r in recs} != EXPECTED_SUBJECTS or len(recs) != 10:
        raise ValueError("Loaded recordings do not match S1-S10.")

    print("=== RANDOM FOREST EXPERIMENT ===")
    print("Data loaded successfully!")
    print("Subjects:", sorted(EXPECTED_SUBJECTS))
    print("Number of recordings:", len(recs))

    print("\n=== RF PARAMETER CHECK ===")

    for value in ["sqrt", "log2", 0.5, 1.0]:
        model = create_rf_model(value)
        rf = model.named_steps["clf"]

        print(
            f"max_features={rf.max_features}, "
            f"max_depth={rf.max_depth}, "
            f"min_samples_leaf={rf.min_samples_leaf}, "
            f"n_estimators={rf.n_estimators}"
        )

    evaluate_rf_models(track, recs)


if __name__ == "__main__":
    main()

