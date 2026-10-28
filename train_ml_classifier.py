
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Find and load our dataset
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "ml_training_dataset.csv"

df = pd.read_csv(DATA_FILE)

# 2. Separate the inputs from the answers
X = df[
    ["latency_ms", "tool_failure", "transcription_mismatch"]
]

y = df["failure_type"]

# 3. Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# 4. Create the Decision Tree
model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42,
)

# 5. Train the model
model.fit(X_train, y_train)

# 6. Make predictions on unseen test records
predictions = model.predict(X_test)

# 7. Evaluate the predictions
accuracy = accuracy_score(y_test, predictions)

print("DECISION TREE CLASSIFIER RESULTS")
print("=" * 45)
print("Total records:", len(df))
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print(f"Accuracy: {accuracy:.2%}")

print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))
