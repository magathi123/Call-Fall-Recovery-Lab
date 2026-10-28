
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

ML_FILE = DATA_DIR / "ml_recovery_recommendations_v2.csv"
OUTPUT_FILE = DATA_DIR / "ml_recovery_simulation_results_v2.csv"

# --------------------------------------------------
# 2. RECOVERY ACTIONS
# --------------------------------------------------

RECOVERY_ACTIONS = {
    "speech_recognition_mismatch":
        "request_value_confirmation",

    "technical_failure":
        "check_service_and_transaction_status",

    "high_latency":
        "inspect_latency_and_processing_state",

    "possible_context_loss":
        "restore_context_and_confirm",

    "no_failure":
        "no_recovery_needed_monitor_normally",
}

# --------------------------------------------------
# 3. SIMULATE A RECOVERY
# --------------------------------------------------

def simulate_recovery(row):
    category = row["failure_category"]
    action = RECOVERY_ACTIONS.get(category, "manual_investigation")

    # No failure predicted
    if category == "no_failure":
        return {
            "simulated_action": action,
            "simulated_outcome": "no_recovery_required",
            "resolution_status": "not_applicable",
            "simulation_evidence": (
                "The model predicted no failure; "
                "normal monitoring is recommended."
            ),
        }

    # Speech recognition mismatch
    if category == "speech_recognition_mismatch":
        return {
            "simulated_action": action,
            "simulated_outcome": "awaiting_customer_confirmation",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "The system requests confirmation before "
                "using the potentially incorrect value."
            ),
        }

    # Technical failure
    if category == "technical_failure":
        return {
            "simulated_action": action,
            "simulated_outcome": "transaction_status_requires_check",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "The transaction status is not available in "
                "the ML output. Check status before retrying."
            ),
        }

    # High latency
    if category == "high_latency":
        return {
            "simulated_action": action,
            "simulated_outcome": "processing_state_requires_check",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "The model predicted high latency, but the "
                "ML output does not confirm whether processing "
                "has completed."
            ),
        }

    # Context loss
    if category == "possible_context_loss":
        return {
            "simulated_action": action,
            "simulated_outcome": "context_restoration_required",
            "resolution_status": "unresolved_in_simulation",
            "simulation_evidence": (
                "Possible context loss was detected. The "
                "simulation requires context restoration and "
                "a response that uses the restored context."
            ),
        }

    # Unknown failure category
    return {
        "simulated_action": action,
        "simulated_outcome": "manual_investigation_required",
        "resolution_status": "unresolved_in_simulation",
        "simulation_evidence": "Unsupported failure category.",
    }


# --------------------------------------------------
# 4. LOAD ML PREDICTIONS
# --------------------------------------------------

if not ML_FILE.exists():
    raise FileNotFoundError(
        f"ML predictions file not found: {ML_FILE}\n"
        "Run ml_recovery_integration_v2.py first."
    )

ml_results = pd.read_csv(ML_FILE)

required_columns = [
    "call_id",
    "ml_prediction",
    "failure_category",
    "recommended_action",
]

missing_columns = [
    column for column in required_columns
    if column not in ml_results.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns in ML file: {missing_columns}"
    )

# --------------------------------------------------
# 5. CONNECT ML TO THE SIMULATOR
# --------------------------------------------------

simulation_results = []

for _, row in ml_results.iterrows():
    result = simulate_recovery(row)

    simulation_results.append({
        "call_id": row["call_id"],
        "ml_prediction": row["ml_prediction"],
        "failure_category": row["failure_category"],
        "ml_recommended_action": row["recommended_action"],
        "simulated_action": result["simulated_action"],
        "simulated_outcome": result["simulated_outcome"],
        "resolution_status": result["resolution_status"],
        "simulation_evidence": result["simulation_evidence"],
    })

output = pd.DataFrame(simulation_results)

# --------------------------------------------------
# 6. SAVE RESULTS WITHOUT OVERWRITING OLD FILES
# --------------------------------------------------

output.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 7. DISPLAY RESULTS
# --------------------------------------------------

print("\nML-DRIVEN RECOVERY SIMULATION")
print("=" * 60)

print(output.to_string(index=False))

print("\nSIMULATION SUMMARY")
print("=" * 60)

print(
    output["resolution_status"]
    .value_counts()
    .to_string()
)

print("\nResults saved to:")
print(OUTPUT_FILE)

