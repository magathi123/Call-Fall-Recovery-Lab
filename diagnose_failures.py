
import csv
from pathlib import Path

DATA_PATH = Path("data") / "test_cases.csv"
RESULTS_PATH = Path("data") / "recovery_results.csv"

with DATA_PATH.open("r", encoding="utf-8", newline="") as file:
    cases = {
        row["case_id"]: row
        for row in csv.DictReader(file)
    }

with RESULTS_PATH.open("r", encoding="utf-8", newline="") as file:
    results = list(csv.DictReader(file))

print("=" * 60)
print("VOICE FAILURE DIAGNOSTICS")
print("=" * 60)

for case_id in ["VOICE001_V1", "VOICE001_V2"]:
    case = cases.get(case_id)

    if not case:
        print(f"\nCase not found: {case_id}")
        continue

    print(f"\nCase ID: {case_id}")
    print(f"User message: {case['user_message']}")
    print(f"Failure type: {case['failure_type']}")
    print(f"Severity: {case['severity']}")
    print(f"Expected behavior: {case['expected_behavior']}")
    print(f"Expected outcome: {case['expected_outcome']}")
    print(f"Baseline latency (ms): {case['baseline_latency_ms']}")

    for result in results:
        if result["case_id"] == case_id:
            print(
                f"  {result['strategy']}: "
                f"passed={result['passed']}, "
                f"reason={result['reason']}"
            )

print("\nDiagnosis complete.")
