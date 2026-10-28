
import pandas as pd
from pathlib import Path
from sklearn.tree import export_text, plot_tree
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "data" / "ml_training_dataset.csv"

df = pd.read_csv(DATA_FILE)

X = df[
    ["latency_ms", "tool_failure", "transcription_mismatch"]
]
y = df["failure_type"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Print the decision rules learned by the model
print("LEARNED DECISION TREE RULES")
print("=" * 45)
print(export_text(model, feature_names=list(X.columns)))

# Show which features the model relied on
importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_,
}).sort_values("importance", ascending=False)

print("\nFEATURE IMPORTANCE")
print(importance.to_string(index=False))

# Save a visual diagram of the trained tree
plt.figure(figsize=(16, 9))
plot_tree(
    model,
    feature_names=list(X.columns),
    class_names=model.classes_,
    filled=True,
    rounded=True,
)
plt.tight_layout()

output_file = PROJECT_DIR / "decision_tree_visualization.png"
plt.savefig(output_file, dpi=150)
plt.close()

print("\nTree image saved to:", output_file)
