
import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier

# Project paths
DATA_DIR = Path(__file__).resolve().parent / "data"

TRAIN_FILE = DATA_DIR / "ml_training_dataset.csv"
TEST_FILE = DATA_DIR / "independent_test_cases.csv"
OUTPUT_FILE = DATA_DIR / "recovery_action_evaluation.csv"

# Load the training data and independent test cases
train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

features = [
    "latency_ms",
    "tool_failure",
    "transcription_mismatch"
]

target = "failure_type"

# Train the model on the original training dataset
model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

model.fit(train_df[features], train_df[target])

# Predict failure categories for the independent test cases
results = test_df.copy()
results["predicted_failure_type"] = model.predict(test_df[features])

# Map each predicted category to a recovery action
recovery_actions = {
    "no_failure": "no_recovery_needed",
    "high_latency": "inspect_latency_and_processing_state",
    "technical_failure": "check_service_and_transaction_status",
    "speech_mismatch": "request_value_confirmation"
}

# Map the expected diagnosis to its corresponding expected action
results["recommended_action"] = results[
    "predicted_failure_type"
].map(recovery_actions)

results["expected_action"] = results[
    "expected_failure_type"
].map(recovery_actions)

# Evaluate the diagnosis and the action separately
results["diagnosis_correct"] = (
    results["predicted_failure_type"]
    == results["expected_failure_type"]
)

results["action_mapping_correct"] = (
    results["recommended_action"]
    == results["expected_action"]
)

# An end-to-end pass requires both the diagnosis and action to be correct
results["end_to_end_correct"] = (
    results["diagnosis_correct"]
    & results["action_mapping_correct"]
)

# Flag cases for review instead of assuming recovery succeeded
results["needs_review"] = ~results["end_to_end_correct"]

# Save detailed results without changing existing files
results.to_csv(OUTPUT_FILE, index=False)

# Print evaluation summary
total = len(results)
diagnosis_correct = int(results["diagnosis_correct"].sum())
actions_correct = int(results["action_mapping_correct"].sum())
end_to_end_correct = int(results["end_to_end_correct"].sum())

print("\n" + "=" * 58)
print("RECOVERY ACTION EVALUATION")
print("=" * 58)

print(f"Test cases: {total}")
print(
    f"Correct diagnoses: {diagnosis_correct}/{total} "
    f"({diagnosis_correct / total:.1%})"
)
print(
    f"Correct action mappings: {actions_correct}/{total} "
    f"({actions_correct / total:.1%})"
)
print(
    f"End-to-end evaluation passes: {end_to_end_correct}/{total} "
    f"({end_to_end_correct / total:.1%})"
)

print("\nCASE-BY-CASE RESULTS")
columns_to_show = [
    "scenario_note",
    "expected_failure_type",
    "predicted_failure_type",
    "recommended_action",
    "diagnosis_correct",
    "action_mapping_correct",
    "needs_review"
]

print(results[columns_to_show].to_string(index=False))

print(f"\nDetailed report saved to:\n{OUTPUT_FILE}")
