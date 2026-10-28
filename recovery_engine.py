
import csv
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_PATH = Path("data") / "test_cases.csv"
OUTPUT_PATH = Path("data") / "recovery_results.csv"

STRATEGIES = ["baseline", "retry", "context_safe"]


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

def load_cases():
    """Load synthetic AI-agent test cases from CSV."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Run: py generate_dataset.py"
        )

    with DATA_PATH.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        cases = list(csv.DictReader(file))

    if not cases:
        raise ValueError("The dataset is empty.")

    return cases


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def baseline_passed(case):
    """Read the synthetic baseline outcome."""

    return case["baseline_passed"].strip().lower() == "true"


def contains_any(text, keywords):
    """Check whether text contains any specified keyword."""

    return any(keyword in text for keyword in keywords)


# --------------------------------------------------
# RECOVERY ENGINE
# --------------------------------------------------

def recover_case(case, strategy):
    """
    Simulate a recovery strategy on a synthetic test case.

    Returns:
        passed (bool): simulated outcome
        reason (str): explanation of the outcome

    Note:
        This is a deterministic rule-based simulation.
        It does not call a real AI model or external API.
    """

    failure_type = case["failure_type"].strip().lower()
    expected = case["expected_behavior"].strip().lower()
    message = case["user_message"].strip().lower()
    context = case["conversation_context"].strip().lower()

    original_passed = baseline_passed(case)

    # ----------------------------------------------
    # STRATEGY 1: BASELINE
    # ----------------------------------------------

    if strategy == "baseline":
        return (
            original_passed,
            "Original synthetic baseline outcome",
        )

    # ----------------------------------------------
    # STRATEGY 2: RETRY
    # ----------------------------------------------

    if strategy == "retry":

        # A retry is simulated as successful for these
        # transient failure categories.
        if failure_type in {"tool_failure", "retrieval_error"}:
            return (
                True,
                "Simulated retry recovered the failure",
            )

        return (
            original_passed,
            "Retry did not address this failure category",
        )

    # ----------------------------------------------
    # STRATEGY 3: CONTEXT-AWARE, SAFETY-FIRST
    # ----------------------------------------------

    if strategy == "context_safe":

        # 1. Handle unsafe responses.
        # Simulate blocking the unsafe response and
        # returning safe guidance instead.
        if failure_type == "unsafe_response":
            return (
                True,
                "Blocked unsafe output and offered safe guidance",
            )

        # 2. Handle loss of conversation context.
        if failure_type == "context_loss":
            if context:
                return (
                    True,
                    "Restored relevant information from context",
                )

            return (
                False,
                "No usable conversation context was available",
            )

        # 3. Handle misunderstood user intent.
        if failure_type == "intent_misunderstanding":

            # Voice correction: confirm the amount before
            # taking action. This covers both voice cases
            # and other cases with the same requirement.
            if "confirm the amount before taking action" in expected:
                return (
                    True,
                    "Requested confirmation of the corrected amount",
                )

            # General clarification for ambiguous requests.
            clarification_keywords = [
                "help",
                "stuck",
                "next",
                "unable",
            ]

            if contains_any(message, clarification_keywords):
                return (
                    True,
                    "Clarified intent and selected a relevant workflow",
                )

            return (
                False,
                "No matching intent-recovery rule was found",
            )

        # 4. Handle tool and retrieval failures.
        if failure_type in {"tool_failure", "retrieval_error"}:
            return (
                True,
                "Simulated retry with a safe fallback",
            )

        # 5. Handle latency-related failures.
        if failure_type == "latency":
            return (
                True,
                "Simulated faster fallback response",
            )

        # 6. Preserve baseline results for other cases.
        return (
            original_passed,
            "Preserved the original baseline outcome",
        )

    raise ValueError(f"Unknown strategy: {strategy}")


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

def evaluate_cases(cases):
    """Run every test case against every strategy."""

    results = []

    for case in cases:
        for strategy in STRATEGIES:
            passed, reason = recover_case(case, strategy)

            results.append({
                "case_id": case["case_id"],
                "scenario_id": case["scenario_id"],
                "workflow": case["workflow"],
                "failure_type": case["failure_type"],
                "severity": case["severity"],
                "is_regression_case": case["is_regression_case"],
                "strategy": strategy,
                "passed": passed,
                "reason": reason,
                "baseline_latency_ms": case["baseline_latency_ms"],
                "synthetic_cost_usd": case["synthetic_cost_usd"],
            })

    return results


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

def save_results(results):
    """Write detailed evaluation results to CSV."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not results:
        raise ValueError("No evaluation results to save.")

    with OUTPUT_PATH.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)


# --------------------------------------------------
# SUMMARY REPORT
# --------------------------------------------------

def print_summary(cases, results):
    """Print strategy pass rates and overall comparisons."""

    print("=" * 60)
    print("AI AGENT RECOVERY & REGRESSION LAB")
    print("RECOVERY ENGINE RESULTS")
    print("=" * 60)

    print(f"\nTest cases: {len(cases)}")
    print(f"Strategies evaluated: {len(STRATEGIES)}")
    print(f"Total evaluation records: {len(results)}")

    strategy_rates = {}

    for strategy in STRATEGIES:
        strategy_results = [
            row for row in results
            if row["strategy"] == strategy
        ]

        passed_count = sum(
            1 for row in strategy_results if row["passed"]
        )

        total = len(strategy_results)
        pass_rate = (
            passed_count / total * 100 if total else 0
        )

        strategy_rates[strategy] = pass_rate

        print(f"\nStrategy: {strategy}")
        print(f"Passed: {passed_count}/{total}")
        print(f"Failed: {total - passed_count}")
        print(f"Pass rate: {pass_rate:.1f}%")

    baseline_rate = strategy_rates.get("baseline", 0)
    recovery_rate = strategy_rates.get("context_safe", 0)

    print("\n" + "-" * 60)
    print("BASELINE VS CONTEXT-SAFE RECOVERY")
    print("-" * 60)

    print(f"Baseline pass rate: {baseline_rate:.1f}%")
    print(f"Recovery pass rate: {recovery_rate:.1f}%")
    print(
        "Pass-rate change: "
        f"{recovery_rate - baseline_rate:+.1f} percentage points"
    )

    print("\nImportant:")
    print("These results are simulated rule-based outcomes.")
    print("They are not measurements of a real AI agent.")
    print(f"\nDetailed results saved to: {OUTPUT_PATH}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    try:
        cases = load_cases()
        results = evaluate_cases(cases)
        save_results(results)
        print_summary(cases, results)

    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nERROR: {error}")


if __name__ == "__main__":
    main()
