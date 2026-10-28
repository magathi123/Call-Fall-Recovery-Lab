
from pathlib import Path
import pandas as pd

# 1. Find the project and data folders.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

# 2. Input and output files.
INPUT_FILE = DATA_DIR / "failure_case_library.csv"
OUTPUT_FILE = DATA_DIR / "recovery_results.csv"


# 3. Define a recovery action for each failure type.
RECOVERY_RULES = {
    "speech_recognition_mismatch": {
        "action": "request_value_confirmation",
        "reason": "The transcript may contain an incorrect critical value.",
        "success_criteria": "Customer confirms the intended value before proceeding.",
        "safe_to_auto_retry": False,
    },
    "technical_failure": {
        "action": "check_service_and_transaction_status",
        "reason": "The connected service reported a failure or timeout.",
        "success_criteria": "Service status is checked and the transaction outcome is known.",
        "safe_to_auto_retry": False,
    },
    "high_latency": {
        "action": "inspect_latency_and_processing_state",
        "reason": "The event exceeded the configured latency threshold.",
        "success_criteria": "The delay is investigated and the workflow reaches a known state.",
        "safe_to_auto_retry": False,
    },
    "stalled_processing": {
        "action": "check_pending_task_status",
        "reason": "Processing may have stalled without a final response.",
        "success_criteria": "The task status is checked before any retry.",
        "safe_to_auto_retry": False,
    },
    "possible_context_loss": {
        "action": "restore_context_and_confirm",
        "reason": "The agent may have failed to use information already provided.",
        "success_criteria": "The agent uses the known information or asks only for necessary clarification.",
        "safe_to_auto_retry": False,
    },
}


# 4. Read the diagnosed cases.
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}. "
        "Run build_failure_case_library.py first."
    )

cases = pd.read_csv(INPUT_FILE)

# 5. Convert each case into a recovery recommendation.
results = []

for _, case in cases.iterrows():
    failure_type = case["failure_type"]
    rule = RECOVERY_RULES.get(failure_type)

    if rule is None:
        action = "manual_investigation"
        reason = "No specific recovery rule is configured for this failure type."
        success_criteria = "An investigator documents the cause and verifies the outcome."
        safe_to_auto_retry = False
    else:
        action = rule["action"]
        reason = rule["reason"]
        success_criteria = rule["success_criteria"]
        safe_to_auto_retry = rule["safe_to_auto_retry"]

    results.append({
        "case_id": case["case_id"],
        "source_call_id": case["source_call_id"],
        "failure_type": failure_type,
        "observed_evidence": case["observed_evidence"],
        "recommended_action": action,
        "action_reason": reason,
        "success_criteria": success_criteria,
        "safe_to_auto_retry": safe_to_auto_retry,
        "execution_status": "recommendation_only",
        "validation_status": "not_tested",
    })


# 6. Save the recovery recommendations.
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_FILE, index=False)

print("RECOVERY ENGINE COMPLETED")
print("=" * 50)
print(f"Cases processed: {len(results_df)}")
print(f"Output file: {OUTPUT_FILE}")
print("\nRecommended actions:")
print(
    results_df[
        [
            "case_id",
            "failure_type",
            "recommended_action",
            "execution_status",
            "validation_status",
        ]
    ].to_string(index=False)
)
