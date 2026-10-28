
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

# --------------------------------------------------
# 1. Locate the project files
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

TRAINING_FILE = DATA_DIR / "ml_training_dataset.csv"
CALL_EVENTS_FILE = DATA_DIR / "voice_call_events.csv"

OUTPUT_FILE = DATA_DIR / "ml_recovery_recommendations.csv"


# --------------------------------------------------
# 2. Train the ML classifier
# --------------------------------------------------

training_data = pd.read_csv(TRAINING_FILE)

features = [
    "latency_ms",
    "tool_failure",
    "transcription_mismatch",
]

X = training_data[features]
y = training_data["failure_type"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42,
)

model.fit(X_train, y_train)

print("ML classifier trained successfully.")


# --------------------------------------------------
# 3. Load existing voice-call events
# --------------------------------------------------

events = pd.read_csv(CALL_EVENTS_FILE)

events["latency_ms"] = pd.to_numeric(
    events["latency_ms"], errors="coerce"
)

results = []


# --------------------------------------------------
# 4. Analyze each call and predict its failure
# --------------------------------------------------

for call_id, call_events in events.groupby("call_id"):

    latency = call_events["latency_ms"].max()
    latency = 0 if pd.isna(latency) else int(latency)

    status_text = (
        call_events["status"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    details_text = (
        call_events["details"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    all_details = " ".join(details_text.tolist())

    # Identify possible tool or service failures.
    tool_failure = int(
        status_text.str.contains(
            r"fail|error|timeout", regex=True
        ).any()
        or details_text.str.contains(
            r"service timeout|tool failure|tool error",
            regex=True,
        ).any()
    )

    # Identify a possible speech/transcription mismatch.
    transcription_mismatch = int(
        details_text.str.contains(
            r"transcription mismatch|amount mismatch|speech recognition mismatch",
            regex=True,
        ).any()
    )

    # The current ML model does not have a context-loss class.
    # Keep this known issue covered by an explicit safety rule.
    context_loss = (
        "repeated question already answered" in all_details
        or "possible context loss" in all_details
    )

    input_data = pd.DataFrame([{
        "latency_ms": latency,
        "tool_failure": tool_failure,
        "transcription_mismatch": transcription_mismatch,
    }])

    predicted_failure = model.predict(input_data)[0]

    # --------------------------------------------------
    # 5. Select a safe recovery recommendation
    # --------------------------------------------------

    if context_loss:
        failure_category = "possible_context_loss"
        action = "restore_context_and_confirm"

    elif predicted_failure == "speech_mismatch":
        failure_category = "speech_recognition_mismatch"
        action = "request_value_confirmation"

    elif predicted_failure == "technical_failure":
        failure_category = "technical_failure"
        action = "check_service_and_transaction_status"

    elif predicted_failure == "high_latency":
        failure_category = "high_latency"
        action = "inspect_latency_and_processing_state"

    else:
        failure_category = "no_failure"
        action = "no_recovery_needed_monitor_normally"

    results.append({
        "call_id": call_id,
        "latency_ms": latency,
        "tool_failure": tool_failure,
        "transcription_mismatch": transcription_mismatch,
        "ml_prediction": predicted_failure,
        "failure_category": failure_category,
        "recommended_action": action,
        "context_loss_rule_applied": context_loss,
        "actual_failure_resolved": "not_verified",
    })


# --------------------------------------------------
# 6. Save results to a NEW file
# --------------------------------------------------

output = pd.DataFrame(results)
output.to_csv(OUTPUT_FILE, index=False)

print("\nML + RECOVERY INTEGRATION RESULTS")
print("=" * 50)
print(output.to_string(index=False))

print("\nPredicted categories:")
print(output["failure_category"].value_counts().to_string())

print("\nSaved results to:")
print(OUTPUT_FILE)
