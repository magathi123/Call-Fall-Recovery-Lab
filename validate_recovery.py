
from pathlib import Path
import pandas as pd

# 1. Locate project files.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

INPUT_FILE = DATA_DIR / "recovery_results.csv"
OUTPUT_FILE = DATA_DIR / "recovery_validation_results.csv"


# 2. Define what a valid recovery recommendation must contain.
VALIDATION_RULES = {
    "speech_recognition_mismatch": {
        "required_action": "request_value_confirmation",
        "evidence": (
            "The recommendation requests confirmation of the critical value "
            "before proceeding."
        ),
    },
    "technical_failure": {
        "required_action": "check_service_and_transaction_status",
        "evidence": (
            "The recommendation checks service and transaction status "
            "before considering a retry."
        ),
    },
    "high_latency": {
        "required_action": "inspect_latency_and_processing_state",
        "evidence": (
            "The recommendation investigates latency and checks whether "
            "processing reaches a known state."
        ),
    },
    "stalled_processing": {
        "required_action": "check_pending_task_status",
        "evidence": (
            "The recommendation checks the pending task before considering "
            "a retry."
        ),
    },
    "possible_context_loss": {
        "required_action": "restore_context_and_confirm",
        "evidence": (
            "The recommendation addresses missing context and verifies "
            "that previously provided information is used appropriately."
        ),
    },
}


# 3. Check that the recovery results file exists.
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. "
        "Run voice_recovery_engine.py first."
    )

results_df = pd.read_csv(INPUT_FILE)

required_columns = {
    "case_id",
    "source_call_id",
    "failure_type",
    "recommended_action",
    "safe_to_auto_retry",
}

missing_columns = required_columns - set(results_df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )


# 4. Validate each recommendation against its predefined rule.
validation_rows = []

for _, case in results_df.iterrows():
    failure_type = case["failure_type"]
    recommended_action = case["recommended_action"]

    rule = VALIDATION_RULES.get(failure_type)

    if rule is None:
        passed = False
        evidence = "No validation rule exists for this failure type."

    elif recommended_action != rule["required_action"]:
        passed = False
        evidence = (
            f"Expected action '{rule['required_action']}' but received "
            f"'{recommended_action}'."
        )

    else:
        passed = True
        evidence = rule["evidence"]

    # This validator does not execute a recovery or contact a live service.
    validation_rows.append({
        "case_id": case["case_id"],
        "source_call_id": case["source_call_id"],
        "failure_type": failure_type,
        "recommended_action": recommended_action,
        "validation_result": (
            "passed_simulated_rule" if passed
            else "failed_simulated_rule"
        ),
        "validation_evidence": evidence,
        "automatic_retry_allowed": False,
        "actual_failure_resolved": "not_verified",
        "test_type": "rule_based_simulation",
    })


# 5. Save results and print a summary.
validation_df = pd.DataFrame(validation_rows)
validation_df.to_csv(OUTPUT_FILE, index=False)

passed_count = (
    validation_df["validation_result"] == "passed_simulated_rule"
).sum()

failed_count = len(validation_df) - passed_count

print("RECOVERY VALIDATION COMPLETED")
print("=" * 55)
print(f"Cases tested: {len(validation_df)}")
print(f"Passed simulated checks: {passed_count}")
print(f"Failed simulated checks: {failed_count}")
print(f"Output file: {OUTPUT_FILE}")

print("\nValidation results:")
print(
    validation_df[
        [
            "case_id",
            "failure_type",
            "validation_result",
            "actual_failure_resolved",
        ]
    ].to_string(index=False)
)

print("\nNote: Passing validates the recommendation rule only.")
print("It does not prove that the real failure was resolved.")
