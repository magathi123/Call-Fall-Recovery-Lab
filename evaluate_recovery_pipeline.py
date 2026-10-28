import pandas as pd
from pathlib import Path

"""
PIPELINE EVALUATION
-------------------
Compares:
1. Rule-based diagnosis report vs ML integration's final failure category.
2. ML recommended action vs V3's expected action.
3. V3 simulated outcomes.

This is a consistency check on synthetic project data, not a measure of
real-world model accuracy or real recovery success.
"""

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

DIAGNOSIS_FILE = DATA_DIR / "call_diagnosis_report.csv"
ML_FILE = DATA_DIR / "ml_recovery_recommendations_v2.csv"
V3_FILE = DATA_DIR / "ml_recovery_simulation_results_v3.csv"

OUTPUT_FILE = DATA_DIR / "pipeline_evaluation_results.csv"


def normalize_diagnosis(value):
    """Map rule-report labels to the categories used by the ML pipeline."""
    value = str(value).strip().lower()

    mapping = {
        "no_failure_detected_by_rules": "no_failure",
        "no_failure": "no_failure",
        "speech_recognition_mismatch": "speech_recognition_mismatch",
        "speech_mismatch": "speech_recognition_mismatch",
        "technical_failure": "technical_failure",
        "high_latency": "high_latency",
        "possible_context_loss": "possible_context_loss",
    }
    return mapping.get(value, value)


def main():
    for file_path in [DIAGNOSIS_FILE, ML_FILE, V3_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path}\n"
                "Make sure the diagnosis report, ML integration output, "
                "and V3 output exist in the data folder."
            )

    diagnosis = pd.read_csv(DIAGNOSIS_FILE)
    ml = pd.read_csv(ML_FILE)
    v3 = pd.read_csv(V3_FILE)

    required_diagnosis = ["call_id", "diagnosis"]
    required_ml = [
        "call_id", "ml_prediction", "failure_category", "recommended_action"
    ]
    required_v3 = [
        "call_id", "action_match", "test_scenario", "resolution_status"
    ]

    for df, required, label in [
        (diagnosis, required_diagnosis, "diagnosis report"),
        (ml, required_ml, "ML output"),
        (v3, required_v3, "V3 output"),
    ]:
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"{label} is missing columns: {missing}")

    # Compare the final category (including the context-loss rule override)
    # with the diagnosis produced by the existing rules-based report.
    diagnosis["reference_category"] = diagnosis["diagnosis"].apply(
        normalize_diagnosis
    )
    ml["normalized_pipeline_category"] = ml["failure_category"].apply(
        normalize_diagnosis
    )

    comparison = diagnosis[
        ["call_id", "diagnosis", "reference_category"]
    ].merge(
        ml[
            [
                "call_id",
                "ml_prediction",
                "failure_category",
                "normalized_pipeline_category",
                "recommended_action",
            ]
        ],
        on="call_id",
        how="outer",
        indicator=True,
    )

    comparison["category_matches_rule_report"] = (
        comparison["reference_category"]
        == comparison["normalized_pipeline_category"]
    )
    comparison.loc[comparison["_merge"] != "both",
                   "category_matches_rule_report"] = False

    # Summarize V3 action mapping once per call, then count scenario outcomes.
    action_check = (
        v3.groupby("call_id")["action_match"]
        .apply(lambda values: all(str(v).strip().lower() == "true" for v in values))
        .rename("v3_action_mapping_passed")
        .reset_index()
    )

    scenario_summary = (
        v3.groupby(["call_id", "resolution_status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    report = comparison.merge(action_check, on="call_id", how="left")
    report = report.merge(scenario_summary, on="call_id", how="left")
    report = report.drop(columns=["_merge"])

    report.to_csv(OUTPUT_FILE, index=False)

    total_calls = len(report)
    category_matches = int(
        report["category_matches_rule_report"].fillna(False).sum()
    )
    action_passes = int(
        report["v3_action_mapping_passed"].fillna(False).sum()
    )

    print("\nPIPELINE EVALUATION REPORT")
    print("=" * 72)
    print(report.to_string(index=False))

    print("\nSUMMARY")
    print("=" * 72)
    print(f"Calls compared: {total_calls}")
    print(
        f"Categories matching existing rule-based diagnosis: "
        f"{category_matches}/{total_calls}"
    )
    print(
        f"Calls passing V3 action-mapping check: "
        f"{action_passes}/{total_calls}"
    )

    print("\nV3 SCENARIO OUTCOMES")
    print("=" * 72)
    print(v3["resolution_status"].value_counts().to_string())

    print("\nInterpretation:")
    print(
        "- Category matching checks consistency with your existing rule-based "
        "diagnosis report; it is not independent ground truth."
    )
    print(
        "- Action mapping checks whether the recommended action matches the "
        "configured action map."
    )
    print(
        "- Resolved/unresolved outcomes come from predefined synthetic "
        "conditions, not real customer interactions."
    )

    print("\nSaved evaluation report to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
