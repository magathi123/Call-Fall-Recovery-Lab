
import pandas as pd
from pathlib import Path

# Find the existing project and data folders
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Create synthetic examples of voice-call behavior
data = [
    # Normal calls
    *[
        {
            "latency_ms": 200 + i * 10,
            "tool_failure": 0,
            "transcription_mismatch": 0,
            "failure_type": "no_failure",
        }
        for i in range(100)
    ],

    # Calls with high latency
    *[
        {
            "latency_ms": 6000 + i * 50,
            "tool_failure": 0,
            "transcription_mismatch": 0,
            "failure_type": "high_latency",
        }
        for i in range(100)
    ],

    # Calls with a technical/tool failure
    *[
        {
            "latency_ms": 200 + i * 10,
            "tool_failure": 1,
            "transcription_mismatch": 0,
            "failure_type": "technical_failure",
        }
        for i in range(100)
    ],

    # Calls with a transcription mismatch
    *[
        {
            "latency_ms": 200 + i * 10,
            "tool_failure": 0,
            "transcription_mismatch": 1,
            "failure_type": "speech_mismatch",
        }
        for i in range(100)
    ],

    # Calls with more than one problem
    *[
        {
            "latency_ms": 6000 + i * 50,
            "tool_failure": 1,
            "transcription_mismatch": 0,
            "failure_type": "technical_failure",
        }
        for i in range(50)
    ],

    *[
        {
            "latency_ms": 6000 + i * 50,
            "tool_failure": 0,
            "transcription_mismatch": 1,
            "failure_type": "speech_mismatch",
        }
        for i in range(50)
    ],
]

# Convert the examples into a table
df = pd.DataFrame(data)

# Save the dataset without overwriting your existing files
output_file = DATA_DIR / "ml_training_dataset.csv"
df.to_csv(output_file, index=False)

print("ML DATASET CREATED")
print("-" * 40)
print("Total records:", len(df))
print("\nCategory counts:")
print(df["failure_type"].value_counts())
print("\nSaved to:", output_file)
print("\nFirst five records:")
print(df.head())
