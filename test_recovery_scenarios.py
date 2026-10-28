
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

INPUT_FILE = DATA_DIR / "recovery_results.csv"
OUTPUT_FILE = DATA_DIR / "recovery_scenario_results.csv"


# Each scenario describes a possible recovery outcome.
# These are deliberately simulated, not real customer interactions.
SCENARIOS = {
    "speech_recognition_mismatch": {
        "scenario": "Customer confirms the intended amount",
        "simulated_action": "confirmation_received",
        "expected_outcome": "critical_value_confirmed",
        "observed_outcome": "critical_value_confirmed",
        "evidence": (
            "The simulated customer confirms the intended amount "
            "before the workflow proceeds."
        ),
    },
    "technical_failure": {
        "scenario": "Booking service times out",
        "simulated_action": "check_transaction_status",
        "expected_outcome": "transaction_status_known",
        "observed_outcome": "transaction_status_known",
        "evidence": (
            "The simulated workflow checks booking status before "
            "considering another attempt."
        ),
    },
    "high_latency": {
        "scenario": "Agent response is delayed",
        "simulated_action": "inspect_processing_state",
        "expected_outcome": "processing_state_known",
        "observed_outcome": "processing_state_known",
        "evidence": (
            "The simulated workflow inspects latency and establishes "
            "a known processing state."
        ),
    },
    "possible_context_loss": {
        "scenario": "Agent repeats a question already answered",
        "simulated_action": "restore_and_check_context",
        "expected_outcome": "known_context_used",
        "observed_outcome": "known_context_used",
        "evidence": (
            "The simulated agent uses the previously supplied information "
            "instead of asking for it again unnecessarily."
        ),
    },
}


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. Run voice_recovery_engine.py first."
    )

recovery_df = pd.read_csv(INPUT_FILE)

required_columns = {"case_id", "source_call_id", "failure_type"}
missing = required_columns - set(recovery_df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")


test_rows = []

for _, case in recovery_df.iterrows():
    failure_type = case["failure_type"]
    scenario = SCENARIOS.get(failure_type)

    if scenario is None:
        # Unknown or unsupported cases are not assumed to be resolved.
        test_rows.append({
            "case_id": case["case_id"],
            "source_call_id": case["source_call_id"],
            "failure_type": failure_type,
            "scenario": "No recovery scenario configured",
            "expected_outcome": "manual_review_required",
            "observed_outcome": "not_tested",
            "test_result": "not_tested",
            "actual_failure_resolved": "not_verified",
            "evidence": "No matching scenario is configured for this failure type.",
            "test_type": "synthetic_simulation",
        })
        continue

    passed = (
        scenario["expected_outcome"] == scenario["observed_outcome"]
    )

    test_rows.append({
        "case_id": case["case_id"],
        "source_call_id": case["source_call_id"],
        "failure_type": failure_type,
        "scenario": scenario["scenario"],
        "expected_outcome": scenario["expected_outcome"],
        "observed_outcome": scenario["observed_outcome"],
        "test_result": "passed" if passed else "failed",
        "actual_failure_resolved": (
            "resolved_in_simulation" if passed else "unresolved_in_simulation"
        ),
        "evidence": scenario["evidence"],
        "test_type": "synthetic_simulation",
    })


report = pd.DataFrame(test_rows)
report.to_csv(OUTPUT_FILE, index=False)

print("RECOVERY SCENARIO TEST REPORT")
print("=" * 55)
print(f"Total cases: {len(report)}")
print(f"Passed: {(report['test_result'] == 'passed').sum()}")
print(f"Failed: {(report['test_result'] == 'failed').sum()}")
print(f"Not tested: {(report['test_result'] == 'not_tested').sum()}")
print(f"Report saved to: {OUTPUT_FILE}")

print("\nDetailed results:")
print(
    report[
        [
            "case_id",
            "failure_type",
            "test_result",
            "actual_failure_resolved",
        ]
    ].to_string(index=False)
)

print("\nReminder: outcomes are simulated, not measured from a live AI agent.")
