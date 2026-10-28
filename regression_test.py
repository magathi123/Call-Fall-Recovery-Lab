
import csv
from pathlib import Path

DATA_PATH = Path("data") / "test_cases.csv"
RESULTS_PATH = Path("data") / "recovery_results.csv"


def load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def main():
    cases = load_csv(DATA_PATH)
    results = load_csv(RESULTS_PATH)

    # Focus on cases explicitly marked for regression testing.
    regression_cases = {
        case["case_id"]: case
        for case in cases
        if case["is_regression_case"].lower() == "true"
    }

    # Compare original and recovered outcomes for each case.
    baseline = {
        row["case_id"]: row
        for row in results
        if row["strategy"] == "baseline"
    }

    recovered = {
        row["case_id"]: row
        for row in results
        if row["strategy"] == "context_safe"
    }

    regressions = []
    recovered_failures = []
    fixed_cases = []

    for case_id, case in regression_cases.items():
        before = baseline[case_id]["passed"].lower() == "true"
        after = recovered[case_id]["passed"].lower() == "true"

        if before and not after:
            regressions.append(case_id)
        elif not after:
            recovered_failures.append(case_id)
        elif not before and after:
            fixed_cases.append(case_id)

    print("=" * 55)
    print("REGRESSION TEST REPORT")
    print("=" * 55)
    print(f"Regression cases checked: {len(regression_cases)}")
    print(f"Previously failing cases fixed: {len(fixed_cases)}")
    print(f"New regressions detected: {len(regressions)}")
    print(f"Still failing after recovery: {len(recovered_failures)}")

    if regressions:
        print("\nRegression details:")
        for case_id in regressions:
            print(f"- {case_id}")

    if recovered_failures:
        print("\nCases still failing:")
        for case_id in recovered_failures:
            print(f"- {case_id}")

    print("\nRegression check complete.")


if __name__ == "__main__":
    main()
