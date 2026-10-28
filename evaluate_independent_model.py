
import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Locate the project data folder
DATA_DIR = Path(__file__).resolve().parent / "data"

TRAIN_FILE = DATA_DIR / "ml_training_dataset.csv"
TEST_FILE = DATA_DIR / "independent_test_cases.csv"
OUTPUT_FILE = DATA_DIR / "independent_evaluation_results.csv"

# 1. Load the training and independent test datasets
train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

features = [
    "latency_ms",
    "tool_failure",
    "transcription_mismatch"
]

target = "failure_type"

# 2. Train the Decision Tree using the original training dataset
model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

model.fit(train_df[features], train_df[target])

# 3. Predict failure categories for the new test cases
predictions = model.predict(test_df[features])

# 4. Compare predictions with our expected diagnoses
actual = test_df["expected_failure_type"]

accuracy = accuracy_score(actual, predictions)

print("\n" + "=" * 55)
print("INDEPENDENT SCENARIO EVALUATION")
print("=" * 55)

print(f"Test cases evaluated: {len(test_df)}")
print(f"Correct predictions: {(actual == predictions).sum()}")
print(f"Scenario accuracy: {accuracy:.2%}")

print("\nCLASSIFICATION REPORT")
print(classification_report(
    actual,
    predictions,
    labels=[
        "no_failure",
        "high_latency",
        "technical_failure",
        "speech_mismatch"
    ],
    zero_division=0
))

print("\nCONFUSION MATRIX")
labels = [
    "no_failure",
    "high_latency",
    "technical_failure",
    "speech_mismatch"
]

matrix = confusion_matrix(actual, predictions, labels=labels)

print("Class order:", labels)
print(matrix)

# 5. Save predictions alongside the expected diagnoses
results = test_df.copy()
results["predicted_failure_type"] = predictions
results["prediction_correct"] = (
    results["expected_failure_type"]
    == results["predicted_failure_type"]
)

results.to_csv(OUTPUT_FILE, index=False)

print(f"\nDetailed results saved to:\n{OUTPUT_FILE}")

print("\nCASE-BY-CASE RESULTS")
print(
    results[
        [
            "scenario_note",
            "expected_failure_type",
            "predicted_failure_type",
            "prediction_correct"
        ]
    ].to_string(index=False)
)
