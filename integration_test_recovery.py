
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

INPUT_FILE = DATA_DIR / "recovery_results.csv"
OUTPUT_FILE = DATA_DIR / "integration_test_results.csv"


# These scenarios describe the state of a workflow AFTER a failure.
# We test both honest and incorrect claims of successful recovery.
SCENARIOS = [
    {
        "scenario_id": "INT_001",
        "failure_type": "speech_recognition_mismatch",
        "scenario": "Amount has not been confirmed",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": False,
    },
    {
        "scenario_id": "INT_002",
        "failure_type": "speech_recognition_mismatch",
        "scenario": "Amount has not been confirmed",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": True,
    },
    {
        "scenario_id": "INT_003",
        "failure_type": "technical_failure",
        "scenario": "Booking status is unknown after timeout",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": False,
    },
    {
        "scenario_id": "INT_004",
        "failure_type": "technical_failure",
        "scenario": "Booking status is unknown after timeout",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": True,
    },
    {
        "scenario_id": "INT_005",
        "failure_type": "high_latency",
        "scenario": "Processing remains incomplete",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": False,
    },
    {
        "scenario_id": "INT_006",
        "failure_type": "high_latency",
        "scenario": "Processing remains incomplete",
        "customer_confirmed": False,
        "transaction_status": "unknown",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": True,
    },
    {
        "scenario_id": "INT_007",
        "failure_type": "possible_context_loss",
        "scenario": "Context has not been restored",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": False,
    },
    {
        "scenario_id": "INT_008",
        "failure_type": "possible_context_loss",
        "scenario": "Context has not been restored",
        "customer_confirmed": False,
        "transaction_status": "not_applicable",
        "processing_complete": False,
        "context_restored": False,
        "claims_resolved": True,
    },
]


# Read decisions from the existing recovery engine's output.
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. "
        "Run voice_recovery_engine.py first."
    )

recovery_df = pd.read_csv(INPUT_FILE)

required_columns = {"failure_type", "recommended_action"}
missing = required_columns - set(recovery_df.columns)

if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

# Build a lookup of the actions the engine actually recommended.
action_lookup = (
    recovery_df
    .drop_duplicates(subset=["failure_type"])
    .set_index("failure_type")["recommended_action"]
    .to_dict()
)


# Define the safety conditions that each action must satisfy.
EXPECTED_ACTIONS = {
    "speech_recognition_mismatch": "request_value_confirmation",
    "technical_failure": "check_service_and_transaction_status",
    "high_latency": "inspect_latency_and_processing_state",
    "possible_context_loss": "restore_context_and_confirm",
}


def validate_scenario(scenario, action):
    failure_type = scenario["failure_type"]
    expected_action = EXPECTED_ACTIONS.get(failure_type)

    # Check whether the engine chose the appropriate action.
    if expected_action is None:
        return False, "No expected action is configured."

    if action != expected_action:
        return False, (
            f"Incorrect action: expected {expected_action}, received {action}."
        )

    # Check whether the system is claiming more than the evidence supports.
    if (
        failure_type == "speech_recognition_mismatch"
        and not scenario["customer_confirmed"]
        and scenario["claims_resolved"]
    ):
        return False, "Cannot claim recovery before amount confirmation."

    if (
        failure_type == "technical_failure"
        and scenario["transaction_status"] == "unknown"
        and scenario["claims_resolved"]
    ):
        return False, "Cannot claim recovery while transaction status is unknown."

    if (
        failure_type == "high_latency"
        and not scenario["processing_complete"]
        and scenario["claims_resolved"]
    ):
        return False, "Cannot claim recovery while processing is incomplete."

    if (
        failure_type == "possible_context_loss"
        and not scenario["context_restored"]
        and scenario["claims_resolved"]
    ):
        return False, "Cannot claim context recovery before context is restored."

    return True, "Action matches the configured rule and the outcome claim is safe."


# Run integration checks.
results = []

for scenario in SCENARIOS:
    failure_type = scenario["failure_type"]
    action = action_lookup.get(failure_type)

    if action is None:
        passed = False
        evidence = "The recovery engine has no recommendation for this failure type."
        action = "no_action_available"
    else:
        passed, evidence = validate_scenario(scenario, action)

    # This describes the simulated scenario, not a live system outcome.
    if scenario["claims_resolved"]:
        resolution_status = (
            "resolved_in_simulation" if passed
            else "unsupported_resolution_claim"
        )
    else:
        resolution_status = "unresolved_in_simulation"

    results.append({
        **scenario,
        "engine_recommended_action": action,
        "integration_test_result": "passed" if passed else "failed",
        "resolution_status": resolution_status,
        "validation_evidence": evidence,
        "test_type": "synthetic_integration_simulation",
    })


report = pd.DataFrame(results)
report.to_csv(OUTPUT_FILE, index=False)

print("INTEGRATED RECOVERY TEST REPORT")
print("=" * 55)
print(f"Total scenarios: {len(report)}")
print(
    f"Passed: {(report['integration_test_result'] == 'passed').sum()}"
)
print(
    f"Failed: {(report['integration_test_result'] == 'failed').sum()}"
)
print(f"Output file: {OUTPUT_FILE}")

print("\nDetailed results:")
print(
    report[
        [
            "scenario_id",
            "failure_type",
            "engine_recommended_action",
            "integration_test_result",
            "resolution_status",
        ]
    ].to_string(index=False)
)

print("\nNote: Results are based on synthetic scenarios and configured rules.")
print("The script does not execute a live agent or verify real-world recovery.")
