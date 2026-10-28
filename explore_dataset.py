
import csv
from collections import Counter
from pathlib import Path

# Locate the generated dataset
DATA_PATH = Path("data") / "test_cases.csv"

with DATA_PATH.open("r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

print("=" * 55)
print("AI AGENT RECOVERY & REGRESSION LAB")
print("DATASET EXPLORATION")
print("=" * 55)

# 1. Dataset dimensions
print(f"\nTotal rows: {len(rows)}")
print(f"Total columns: {len(rows[0]) if rows else 0}")

# 2. Inspect available fields
if rows:
    print("\nColumns:")
    for column in rows[0].keys():
        print(f"- {column}")

# 3. Count failure categories
failure_counts = Counter(
    row["failure_type"] for row in rows
)

print("\nFailure categories:")
for category, count in sorted(failure_counts.items()):
    print(f"{category}: {count}")

# 4. Count severity levels
severity_counts = Counter(
    row["severity"] for row in rows
)

print("\nSeverity distribution:")
for severity, count in sorted(severity_counts.items()):
    print(f"{severity}: {count}")

# 5. Check for duplicate test case IDs
case_ids = [row["case_id"] for row in rows]
duplicate_ids = len(case_ids) - len(set(case_ids))

print(f"\nDuplicate case IDs: {duplicate_ids}")

# 6. Check missing values
missing_values = sum(
    1
    for row in rows
    for value in row.values()
    if value is None or not value.strip()
)

print(f"Missing field values: {missing_values}")

print("\nDataset exploration complete!")
