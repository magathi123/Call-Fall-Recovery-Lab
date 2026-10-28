
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "recovery_simulation_results.csv"


# --------------------------------------------------
# 1. Synthetic scenarios for testing recovery behavior
# --------------------------------------------------
SCENARIOS = [
    {
        "scenario_id": "SIM_001",
        "failure_type": "speech_recognition_mismatch",
        "description": "Customer confirms the correct transfer amount",
        "customer_confirmed": True,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_002",
        "failure_type": "speech_recognition_mismatch",
        "description": "Customer does not confirm the transfer amount",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_003",
        "failure_type": "technical_failure",
        "description": "Booking status shows booking already completed",
        "customer_confirmed": False,
        "transaction_status": "already_completed",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_004",
        "failure_type": "technical_failure",
        "description": "Booking status remains unknown after timeout",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_005",
        "failure_type": "high_latency",
        "description": "Processing completes after investigation",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": True,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_006",
        "failure_type": "high_latency",
        "description": "Processing remains incomplete",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
    {
        "scenario_id": "SIM_007",
        "failure_type": "possible_context_loss",
        "description": "Context is restored and used in the response",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": True,
        "response_uses_context": True,
    },
    {
        "scenario_id": "SIM_008",
        "failure_type": "possible_context_loss",
        "description": "Context is not restored",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "response_uses_context": False,
    },
]


# --------------------------------------------------
# 2. Choose a recovery action based on failure type
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
}


# --------------------------------------------------
# 3. Simulate the recovery and evaluate its outcome
# --------------------------------------------------
def simulate_recovery(case):
    failure_type = case["failure_type"]
    action = RECOVERY_ACTIONS.get(failure_type)

    if action is None:
        return {
            "recommended_action": "manual_investigation",
            "simulated_outcome": "unsupported_failure_type",
            "resolution_status": "unsafe_action_detected",
            "evidence": "No recovery rule exists for this failure type.",
        }

    # A. Speech recognition mismatch
    if failure_type == "speech_recognition_mismatch":
        if case["customer_confirmed"]:
            return {
                "recommended_action": action,
                "simulated_outcome": "critical_value_confirmed",
                "resolution_status": "resolved_in_simulation",
                "evidence": (
                    "The customer confirmed the intended value before "
                    "the workflow proceeded."
                ),
            }

        return {
            "recommended_action": action,
            "simulated_outcome": "awaiting_customer_confirmation",
            "resolution_status": "unresolved_in_simulation",
            "evidence": (
                "The transfer remains blocked until the customer "
                "confirms the intended value."
            ),
        }

    # B. Technical failure
    if failure_type == "technical_failure":
        status = case["transaction_status"]

        if status == "already_completed":
            return {
                "recommended_action": action,
                "simulated_outcome": "existing_booking_confirmed",
                "resolution_status": "resolved_in_simulation",
                "evidence": (
                    "The status check found that the booking had already "
                    "completed. No duplicate retry was needed."
                ),
            }

        if status == "confirmed_failed":
            return {
                "recommended_action": action,
                "simulated_outcome": "booking_failure_confirmed",
                "resolution_status": "unresolved_in_simulation",
                "evidence": (
                    "The booking failed. Further recovery requires "
                    "a safe retry decision or manual handling."
                ),
            }

        return {
            "recommended_action": action,
            "simulated_outcome": "transaction_status_unknown",
            "resolution_status": "unresolved_in_simulation",
            "evidence": (
                "The booking status is still unknown. The system must "
                "not blindly retry or claim success."
            ),
        }

    # C. High latency
    if failure_type == "high_latency":
        if case["processing_complete"]:
            return {
                "recommended_action": action,
                "simulated_outcome": "processing_completed",
                "resolution_status": "resolved_in_simulation",
                "evidence": (
                    "The simulated processing task completed and its "
                    "final state was observed."
                ),
            }

        return {
            "recommended_action": action,
            "simulated_outcome": "processing_still_incomplete",
            "resolution_status": "unresolved_in_simulation",
            "evidence": (
                "Processing remains incomplete. The case should stay "
                "open for further investigation."
            ),
        }

    # D. Possible context loss
    if failure_type == "possible_context_loss":
        if case["context_restored"] and case["response_uses_context"]:
            return {
                "recommended_action": action,
                "simulated_outcome": "context_restored_and_used",
                "resolution_status": "resolved_in_simulation",
                "evidence": (
                    "The previously supplied information was restored "
                    "and used in the simulated response."
                ),
            }

        return {
            "recommended_action": action,
            "simulated_outcome": "context_not_verified",
            "resolution_status": "unresolved_in_simulation",
            "evidence": (
                "Context restoration or its use in the response could "
                "not be verified."
            ),
        }


# --------------------------------------------------
# 4. Run all scenarios
# --------------------------------------------------
results = []

for case in SCENARIOS:
    outcome = simulate_recovery(case)

    results.append({
        **case,
        **outcome,
        "test_type": "synthetic_recovery_simulation",
    })


# --------------------------------------------------
# 5. Save the results and print a summary
# --------------------------------------------------
report = pd.DataFrame(results)
report.to_csv(OUTPUT_FILE, index=False)

resolved = (
    report["resolution_status"] == "resolved_in_simulation"
).sum()

unresolved = (
    report["resolution_status"] == "unresolved_in_simulation"
).sum()

unsafe = (
    report["resolution_status"] == "unsafe_action_detected"
).sum()

print("RECOVERY SIMULATOR REPORT")
print("=" * 55)
print(f"Total scenarios: {len(report)}")
print(f"Resolved in simulation: {resolved}")
print(f"Unresolved in simulation: {unresolved}")
print(f"Unsafe action / unsupported rule: {unsafe}")
print(f"Output file: {OUTPUT_FILE}")

print("\nDetailed results:")
print(
    report[
        [
            "scenario_id",
            "failure_type",
            "recommended_action",
            "simulated_outcome",
            "resolution_status",
        ]
    ].to_string(index=False)
)

print("\nNote: All outcomes are synthetic, not live system measurements.")

