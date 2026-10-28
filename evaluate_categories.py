
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# AI AGENT RECOVERY LAB
# Step 6: Failure Category Evaluation
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RESULTS_FILE = DATA_DIR / "recovery_results.csv"
CATEGORY_REPORT_FILE = DATA_DIR / "category_evaluation.csv"


def to_bool(value):
    """Convert CSV boolean values safely into Python booleans."""
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    return str(value).strip().lower() in {
        "true", "1", "yes"
    }


def main():
    if not RESULTS_FILE.exists():
        print(f"ERROR: File not found: {RESULTS_FILE}")
        print("Run recovery_engine.py first.")
        return

    df = pd.read_csv(RESULTS_FILE)

    required_columns = {
        "case_id",
        "failure_type",
        "strategy",
        "passed",
        "is_regression_case",
    }

    missing = required_columns - set(df.columns)

    if missing:
        print("ERROR: Missing required columns:", sorted(missing))
        print("Check the columns in recovery_results.csv.")
        return

    df["passed"] = df["passed"].apply(to_bool)
    df["is_regression_case"] = (
        df["is_regression_case"].apply(to_bool)
    )

    # ----------------------------------------------
    # 1. Performance by failure category and strategy
    # ----------------------------------------------

    category_report = (
        df.groupby(["failure_type", "strategy"], dropna=False)
        .agg(
            total_cases=("case_id", "nunique"),
            passed_cases=("passed", "sum"),
        )
        .reset_index()
    )

    category_report["failed_cases"] = (
        category_report["total_cases"]
        - category_report["passed_cases"]
    )

    category_report["pass_rate_pct"] = (
        category_report["passed_cases"]
        / category_report["total_cases"]
        * 100
    ).round(1)

    category_report = category_report.sort_values(
        ["failure_type", "strategy"]
    )

    category_report.to_csv(CATEGORY_REPORT_FILE, index=False)

    print("\n" + "=" * 65)
    print("FAILURE CATEGORY EVALUATION")
    print("=" * 65)

    print(
        category_report.to_string(
            index=False,
            formatters={
                "pass_rate_pct": lambda value: f"{value:.1f}%"
            },
        )
    )

    # ----------------------------------------------
    # 2. Compare baseline with context_safe recovery
    # ----------------------------------------------

    baseline = (
        df[df["strategy"] == "baseline"][
            ["case_id", "passed", "is_regression_case"]
        ]
        .drop_duplicates(subset=["case_id"])
        .rename(columns={"passed": "baseline_passed"})
    )

    recovered = (
        df[df["strategy"] == "context_safe"][
            ["case_id", "passed"]
        ]
        .drop_duplicates(subset=["case_id"])
        .rename(columns={"passed": "recovered_passed"})
    )

    comparison = baseline.merge(
        recovered,
        on="case_id",
        how="inner",
        validate="one_to_one",
    )

    regression_cases = comparison[
        comparison["is_regression_case"]
    ]

    fixed = (
        ~regression_cases["baseline_passed"]
        & regression_cases["recovered_passed"]
    ).sum()

    new_regressions = (
        regression_cases["baseline_passed"]
        & ~regression_cases["recovered_passed"]
    ).sum()

    still_failing = (
        ~regression_cases["baseline_passed"]
        & ~regression_cases["recovered_passed"]
    ).sum()

    previously_passing = (
        regression_cases["baseline_passed"]
    ).sum()

    print("\n" + "=" * 65)
    print("REGRESSION CONSISTENCY CHECK")
    print("=" * 65)

    print(f"Regression cases checked: {len(regression_cases)}")
    print(f"Previously failing cases fixed: {fixed}")
    print(f"New regressions detected: {new_regressions}")
    print(f"Still failing after recovery: {still_failing}")
    print(f"Already passing at baseline: {previously_passing}")

    accounted_for = (
        fixed
        + new_regressions
        + still_failing
        + previously_passing
    )

    print(f"Cases accounted for: {accounted_for}")

    if accounted_for != len(regression_cases):
        print("WARNING: Regression counts do not reconcile.")
    elif new_regressions == 0 and still_failing == 0:
        print("RESULT: All regression cases pass after recovery.")
    else:
        print("RESULT: Some regression cases need investigation.")

    print("\n" + "=" * 65)
    print("EVALUATION COMPLETE")
    print(f"Category report saved to: {CATEGORY_REPORT_FILE}")
    print("=" * 65)

    print(
        "\nNote: These are results from a synthetic test dataset "
        "and rule-based simulation, not a live AI platform."
    )


if __name__ == "__main__":
    main()
