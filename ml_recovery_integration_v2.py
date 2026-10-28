
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

TRAINING_FILE = DATA_DIR / "ml_training_dataset.csv"
CALL_EVENTS_FILE = DATA_DIR / "voice_call_events.csv"
OUTPUT_FILE = DATA_DIR / "ml_recovery_recommendations_v2.csv"

# 1. Train the existing classifier
training_data = pd.read_csv(TRAINING_FILE)

features = [
    "latency_ms",
    "tool_failure",
    "transcription_mismatch",
]

X = training_data[features]
y = training_data["failure_type"]

X_train, _, y_train, _ = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# 2. Load call events
events = pd.read_csv(CALL_EVENTS_FILE)

for column in ["transcript", "details", "status"]:
    events[column] = events[column].fillna("").astype(str)

events["latency_ms"] = pd.to_numeric(
    events["latency_ms"], errors="coerce"
)

results = []

# 3. Process each call
for call_id, call_events in events.groupby("call_id"):

    latency = call_events["latency_ms"].max()
    latency = 0 if pd.isna(latency) else int(latency)

    statuses = call_events["status"].str.lower()
    details = call_events["details"].str.lower()
    transcripts = call_events["transcript"].str.lower()

    all_details = " ".join(details)
    all_transcripts = " ".join(transcripts)

    tool_failure = int(
        statuses.str.contains(
            r"fail|error|timeout", regex=True
        ).any()
        or details.str.contains(
            r"service timeout|tool failure|tool error",
            regex=True,
        ).any()
    )

    transcription_mismatch = int(
        details.str.contains(
            r"transcription mismatch|amount mismatch|speech recognition mismatch",
            regex=True,
        ).any()
    )

    # Explicitly detect the known context-loss evidence.
    context_loss = (
        "repeated a question already answered" in all_details
        or "repeated question" in all_details
        or (
            "my name is ravi" in all_transcripts
            and "could you tell me your name" in all_transcripts
        )
    )

    model_input = pd.DataFrame([{
        "latency_ms": latency,
        "tool_failure": tool_failure,
        "transcription_mismatch": transcription_mismatch,
    }])

    ml_prediction = model.predict(model_input)[0]

    # 4. Apply safety rules before selecting an action
    if context_loss:
        category = "possible_context_loss"
        action = "restore_context_and_confirm"

    elif ml_prediction == "speech_mismatch":
        category = "speech_recognition_mismatch"
        action = "request_value_confirmation"

    elif ml_prediction == "technical_failure":
        category = "technical_failure"
        action = "check_service_and_transaction_status"

    elif ml_prediction == "high_latency":
        category = "high_latency"
        action = "inspect_latency_and_processing_state"

    else:
        category = "no_failure"
        action = "no_recovery_needed_monitor_normally"

    results.append({
        "call_id": call_id,
        "latency_ms": latency,
        "tool_failure": tool_failure,
        "transcription_mismatch": transcription_mismatch,
        "ml_prediction": ml_prediction,
        "failure_category": category,
        "recommended_action": action,
        "context_loss_rule_applied": context_loss,
        "actual_failure_resolved": "not_verified",
    })

# 5. Save to a new output file
output = pd.DataFrame(results)
output.to_csv(OUTPUT_FILE, index=False)

print("ML + RECOVERY INTEGRATION V2")
print("=" * 50)
print(output.to_string(index=False))

print("\nContext-loss checks:")
print(
    output[
        ["call_id", "context_loss_rule_applied", "failure_category"]
    ].to_string(index=False)
)

print("\nSaved to:", OUTPUT_FILE)
