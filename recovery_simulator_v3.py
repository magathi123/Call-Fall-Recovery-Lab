import pandas as pd
from pathlib import Path

"""
ML-DRIVEN RECOVERY SIMULATOR V3
--------------------------------
Purpose:
1. Read the ML/integration output.
2. Select a recovery action for each diagnosed failure.
3. Test each action against simulated success and failure conditions.
4. Save results to a NEW CSV file.

Important:
- This is a synthetic simulation, not a live voice agent.
- It does not call real APIs or actually book appointments.
- The success/failure conditions are predefined test assumptions.
"""

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

ML_FILE = DATA_DIR / "ml_recovery_recommendations_v2.csv"
OUTPUT_FILE = DATA_DIR / "ml_recovery_simulation_results_v3.csv"

RECOVERY_ACTIONS = {
    "speech_recognition_mismatch": "request_value_confirmation",
    "technical_failure": "check_service_and_transaction_status",
    "high_latency": "inspect_latency_and_processing_state",
    "possible_context_loss": "restore_context_and_confirm",
    "no_failure": "no_recovery_needed_monitor_normally",
}


def simulate_scenario(category, scenario_name, conditions):
    """Evaluate one predefined simulated recovery scenario."""

    action = RECOVERY_ACTIONS.get(category, "manual_investigation")

    if category == "no_failure":
        return {
            "simulated_action": action,
            "simulated_outcome": "no_recovery_required",
            "resolution_status": "not_applicable",
            "simulation_evidence": (
                "No failure was diagnosed; normal monitoring is appropriate."
            ),
        }

    if category == "speech_recognition_mismatch":
        confirmed = conditions["customer_confirmed"]
        if confirmed:
            return {
                "simulated_action": action,
                "simulated_outcome": "corrected_value_confirmed",
                "resolution_status": "resolved_in_simulation",
                "simulation_evidence": (
                    "The customer confirmed the corrected value before proceeding."
                ),
            }
        return {
            "simulated_action": action,
            "simulated_outcome": "awaiting_customer_confirmation",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "The customer did not confirm the corrected value; the workflow must not proceed."
            ),
        }

    if category == "technical_failure":
        status = conditions["transaction_status"]
        if status == "already_completed":
            return {
                "simulated_action": action,
                "simulated_outcome": "existing_transaction_found",
                "resolution_status": "resolved_in_simulation",
                "simulation_evidence": (
                    "The status check found the transaction had already completed; no retry is needed."
                ),
            }
        if status == "confirmed_failed":
            return {
                "simulated_action": action,
                "simulated_outcome": "transaction_confirmed_failed",
                "resolution_status": "unresolved_in_simulation",
                "simulation_evidence": (
                    "The transaction is confirmed failed. A safe retry or fallback requires a separate policy."
                ),
            }
        return {
            "simulated_action": action,
            "simulated_outcome": "transaction_status_unknown",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "The transaction status remains unknown; do not blindly retry."
            ),
        }

    if category == "high_latency":
        if conditions["processing_complete"]:
            return {
                "simulated_action": action,
                "simulated_outcome": "processing_completed",
                "resolution_status": "resolved_in_simulation",
                "simulation_evidence": (
                    "The processing-state check confirms that processing completed."
                ),
            }
        return {
            "simulated_action": action,
            "simulated_outcome": "processing_still_pending",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "Processing is not confirmed complete; continue checking or use a safe fallback."
            ),
        }

    if category == "possible_context_loss":
        if conditions["context_restored"] and conditions["response_uses_context"]:
            return {
                "simulated_action": action,
                "simulated_outcome": "context_restored_and_used",
                "resolution_status": "resolved_in_simulation",
                "simulation_evidence": (
                    "The prior context was restored and the next response used it correctly."
                ),
            }
        return {
            "simulated_action": action,
            "simulated_outcome": "context_not_safely_restored",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "Context restoration and correct use of that context were not both confirmed."
            ),
        }

    return {
        "simulated_action": action,
        "simulated_outcome": "manual_investigation_required",
        "resolution_status": "unresolved_in_simulation",
        "simulation_evidence": "Unsupported failure category; manual investigation is required.",
    }


def scenarios_for(category):
    """Return paired test conditions for a failure category."""
    if category == "speech_recognition_mismatch":
        return [
            ("success_path", {"customer_confirmed": True}),
            ("failure_path", {"customer_confirmed": False}),
        ]
    if category == "technical_failure":
        return [
            ("success_path", {"transaction_status": "already_completed"}),
            ("failure_path", {"transaction_status": "unknown"}),
        ]
    if category == "high_latency":
        return [
            ("success_path", {"processing_complete": True}),
            ("failure_path", {"processing_complete": False}),
        ]
    if category == "possible_context_loss":
        return [
            (
                "success_path",
                {"context_restored": True, "response_uses_context": True},
            ),
            (
                "failure_path",
                {"context_restored": False, "response_uses_context": False},
            ),
        ]
    return [("not_applicable", {})]


def main():
    if not ML_FILE.exists():
        raise FileNotFoundError(
            f"Could not find the ML output file:\n{ML_FILE}\n"
            "Run ml_recovery_integration_v2.py first."
        )

    ml_data = pd.read_csv(ML_FILE)
    required_columns = [
        "call_id",
        "ml_prediction",
        "failure_category",
        "recommended_action",
    ]
    missing = [col for col in required_columns if col not in ml_data.columns]
    if missing:
        raise ValueError(
            f"The ML output is missing required columns: {missing}"
        )

    results = []

    for _, row in ml_data.iterrows():
        category = str(row["failure_category"])
        recommended_action = RECOVERY_ACTIONS.get(
            category, "manual_investigation"
        )

        # Compare the action from the integration output with the V3 action map.
        ml_action = str(row["recommended_action"])
        action_match = ml_action == recommended_action

        for scenario_name, conditions in scenarios_for(category):
            result = simulate_scenario(category, scenario_name, conditions)
            results.append(
                {
                    "call_id": row["call_id"],
                    "ml_prediction": row["ml_prediction"],
                    "failure_category": category,
                    "ml_recommended_action": ml_action,
                    "v3_expected_action": recommended_action,
                    "action_match": action_match,
                    "test_scenario": scenario_name,
                    "simulated_action": result["simulated_action"],
                    "simulated_outcome": result["simulated_outcome"],
                    "resolution_status": result["resolution_status"],
                    "simulation_evidence": result["simulation_evidence"],
                }
            )

    output = pd.DataFrame(results)
    output.to_csv(OUTPUT_FILE, index=False)

    print("\nML-DRIVEN RECOVERY SIMULATOR V3")
    print("=" * 65)
    print(output.to_string(index=False))

    print("\nSUMMARY BY RESOLUTION STATUS")
    print("=" * 65)
    print(output["resolution_status"].value_counts().to_string())

    print("\nSUMMARY BY TEST SCENARIO")
    print("=" * 65)
    print(
        output.groupby(["test_scenario", "resolution_status"])
        .size()
        .rename("case_count")
        .to_string()
    )

    print("\nACTION-MAPPING CHECK")
    print("=" * 65)
    print(output[["call_id", "failure_category", "ml_recommended_action",
                  "v3_expected_action", "action_match"]]
          .drop_duplicates()
          .to_string(index=False))

    print("\nSaved results to:")
    print(OUTPUT_FILE)
    print(
        "\nReminder: these are predefined synthetic test outcomes, "
        "not proof of real-world recovery performance."
    )


if __name__ == "__main__":
    main()
