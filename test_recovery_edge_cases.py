
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "recovery_edge_case_results.csv"

# Each case describes simulated recovery behavior.
# Some cases deliberately contain unsafe behavior to test detection.
EDGE_CASES = [
    {
        "case_id": "EDGE_001",
        "failure_type": "speech_recognition_mismatch",
        "scenario": "Customer does not confirm transfer amount",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "proceed_with_transfer",
        "claims_resolved": True,
    },
    {
        "case_id": "EDGE_002",
        "failure_type": "speech_recognition_mismatch",
        "scenario": "Customer does not confirm transfer amount",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "request_confirmation_and_stop",
        "claims_resolved": False,
    },
    {
        "case_id": "EDGE_003",
        "failure_type": "technical_failure",
        "scenario": "Booking times out; transaction status is unknown",
        "customer_confirmed": True,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "retry_booking_immediately",
        "claims_resolved": True,
    },
    {
        "case_id": "EDGE_004",
        "failure_type": "technical_failure",
        "scenario": "Booking times out; transaction status is unknown",
        "customer_confirmed": True,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "check_booking_status_before_retry",
        "claims_resolved": False,
    },
    {
        "case_id": "EDGE_005",
        "failure_type": "high_latency",
        "scenario": "Processing remains stuck after investigation",
        "customer_confirmed": True,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "report_success",
        "claims_resolved": True,
    },
    {
        "case_id": "EDGE_006",
        "failure_type": "high_latency",
        "scenario": "Processing remains stuck after investigation",
        "customer_confirmed": True,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "report_unresolved_and_escalate",
        "claims_resolved": False,
    },
    {
        "case_id": "EDGE_007",
        "failure_type": "possible_context_loss",
        "scenario": "Agent still lacks previously supplied context",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "proposed_action": "report_success",
        "claims_resolved": True,
    },
    {
        "case_id": "EDGE_008",
        "failure_type": "possible_context_loss",
        "scenario": "Context is restored and checked",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": True,
        "context_restored": True,
        "proposed_action": "verify_context_and_continue",
        "claims_resolved": True,
    },
]


def evaluate_case(case):
    """Return whether the simulated behavior follows safety rules."""

    failure_type = case["failure_type"]
    action = case["proposed_action"]

    # Rule 1: Never proceed with a transfer without confirmation.
    if failure_type == "speech_recognition_mismatch":
        safe = (
            case["customer_confirmed"]
            or action == "request_confirmation_and_stop"
        )

        if not safe:
            return False, "Transfer could proceed without amount confirmation."

        if case["claims_resolved"] and not case["customer_confirmed"]:
            return False, "Resolution was claimed without customer confirmation."

        return True, "Unconfirmed transfer is blocked, or the amount is confirmed."

    # Rule 2: Check transaction status before retrying a timed-out operation.
    if failure_type == "technical_failure":
        if (
            case["transaction_status"] == "unknown"
            and action == "retry_booking_immediately"
        ):
            return False, "Unsafe retry: booking status is still unknown."

        if case["claims_resolved"] and case["transaction_status"] == "unknown":
            return False, "Resolution was claimed while booking status is unknown."

        return True, "The workflow avoids an immediate retry with unknown status."

    # Rule 3: Do not claim recovery while processing is still incomplete.
    if failure_type == "high_latency":
        if case["claims_resolved"] and not case["processing_complete"]:
            return False, "Success was claimed although processing is incomplete."

        return True, "The workflow reports unresolved work or verified completion."

    # Rule 4: Do not claim context recovery unless context was restored.
    if failure_type == "possible_context_loss":
        if case["claims_resolved"] and not case["context_restored"]:
            return False, "Success was claimed although context was not restored."

        return True, "The workflow verifies context before claiming recovery."

    return False, "No safety rule is configured for this failure type."


# Run all simulated edge-case checks.
results = []

for case in EDGE_CASES:
    passed, evidence = evaluate_case(case)

    if case["claims_resolved"]:
        if (
            case["failure_type"] == "speech_recognition_mismatch"
            and not case["customer_confirmed"]
        ):
            resolution_status = "not_verified"
        elif (
            case["failure_type"] == "technical_failure"
            and case["transaction_status"] == "unknown"
        ):
            resolution_status = "not_verified"
        elif (
            case["failure_type"] == "high_latency"
            and not case["processing_complete"]
        ):
            resolution_status = "not_verified"
        elif (
            case["failure_type"] == "possible_context_loss"
            and not case["context_restored"]
        ):
            resolution_status = "not_verified"
        else:
            resolution_status = "resolved_in_simulation"
    else:
        resolution_status = "unresolved_in_simulation"

    results.append({
        **case,
        "test_result": "passed" if passed else "failed",
        "resolution_status": resolution_status,
        "validation_evidence": evidence,
        "test_type": "synthetic_edge_case_simulation",
    })

report = pd.DataFrame(results)
report.to_csv(OUTPUT_FILE, index=False)

print("RECOVERY EDGE-CASE TEST REPORT")
print("=" * 55)
print(f"Total cases: {len(report)}")
print(f"Passed safety checks: {(report['test_result'] == 'passed').sum()}")
print(f"Failed safety checks: {(report['test_result'] == 'failed').sum()}")
print(f"Output file: {OUTPUT_FILE}")

print("\nDetailed results:")
print(
    report[
        [
            "case_id",
            "failure_type",
            "test_result",
            "resolution_status",
            "validation_evidence",
        ]
    ].to_string(index=False)
)

print("\nNote: These are synthetic policy checks, not live agent results.")
