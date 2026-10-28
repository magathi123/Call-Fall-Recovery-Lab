
import pandas as pd
from pathlib import Path

# Save the dataset inside our existing project folder
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

events = [
    # CALL 001: Successful conversation
    ("CALL_001", "10:00:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_001", "10:00:02", 2, "user_speech_detected",
     "I want to check my account balance", 0, "success", ""),
    ("CALL_001", "10:00:03", 3, "transcription_completed",
     "I want to check my account balance", 250, "success", ""),
    ("CALL_001", "10:00:04", 4, "intent_extracted",
     "check account balance", 180, "success", ""),
    ("CALL_001", "10:00:05", 5, "tool_called",
     "", 100, "success", ""),
    ("CALL_001", "10:00:06", 6, "tool_result",
     "Balance retrieved successfully", 400, "success", ""),
    ("CALL_001", "10:00:07", 7, "agent_response",
     "Your balance is 5000 rupees", 300, "success", ""),
    ("CALL_001", "10:00:10", 8, "call_ended",
     "", 0, "normal", "Conversation completed"),

    # CALL 002: Speech recognition misunderstanding
    ("CALL_002", "10:01:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_002", "10:01:02", 2, "user_speech_detected",
     "Transfer fifteen thousand rupees", 0, "success", ""),
    ("CALL_002", "10:01:03", 3, "transcription_completed",
     "Transfer fifty thousand rupees", 700, "success",
     "Possible amount transcription mismatch"),
    ("CALL_002", "10:01:04", 4, "intent_extracted",
     "transfer amount=50000", 200, "success", ""),
    ("CALL_002", "10:01:05", 5, "agent_response",
     "I will transfer fifty thousand rupees", 300, "success",
     "Amount not confirmed"),
    ("CALL_002", "10:01:08", 6, "call_ended",
     "", 0, "unknown", "Call ended before confirmation"),

    # CALL 003: Tool failure
    ("CALL_003", "10:02:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_003", "10:02:02", 2, "user_speech_detected",
     "Book an appointment for tomorrow", 0, "success", ""),
    ("CALL_003", "10:02:03", 3, "transcription_completed",
     "Book an appointment for tomorrow", 300, "success", ""),
    ("CALL_003", "10:02:04", 4, "intent_extracted",
     "book appointment", 150, "success", ""),
    ("CALL_003", "10:02:05", 5, "tool_called",
     "appointment_booking", 100, "success", ""),
    ("CALL_003", "10:02:08", 6, "tool_result",
     "", 3000, "failure", "Booking service timeout"),
    ("CALL_003", "10:02:09", 7, "agent_response",
     "Sorry, I could not complete the booking", 400, "success", ""),
    ("CALL_003", "10:02:15", 8, "call_ended",
     "", 0, "unknown", "Call ended after incomplete workflow"),

    # CALL 004: Slow response
    ("CALL_004", "10:03:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_004", "10:03:02", 2, "user_speech_detected",
     "What are your opening hours?", 0, "success", ""),
    ("CALL_004", "10:03:03", 3, "transcription_completed",
     "What are your opening hours?", 250, "success", ""),
    ("CALL_004", "10:03:04", 4, "intent_extracted",
     "opening hours", 150, "success", ""),
    ("CALL_004", "10:03:15", 5, "agent_response",
     "We are open from nine to five", 11000, "success",
     "Response took 11 seconds"),
    ("CALL_004", "10:03:18", 6, "call_ended",
     "", 0, "normal", "Conversation completed"),

    # CALL 005: Customer hangs up while waiting
    ("CALL_005", "10:04:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_005", "10:04:02", 2, "user_speech_detected",
     "Can you help me update my details?", 0, "success", ""),
    ("CALL_005", "10:04:03", 3, "transcription_completed",
     "Can you help me update my details?", 300, "success", ""),
    ("CALL_005", "10:04:04", 4, "intent_extracted",
     "update customer details", 200, "success", ""),
    ("CALL_005", "10:04:05", 5, "agent_processing",
     "", 15000, "pending", "No response recorded during wait"),
    ("CALL_005", "10:04:20", 6, "call_ended",
     "", 0, "unknown", "Customer or network termination not confirmed"),

    # CALL 006: Context loss
    ("CALL_006", "10:05:00", 1, "call_connected", "", 0, "success", ""),
    ("CALL_006", "10:05:02", 2, "user_speech_detected",
     "My name is Ravi and I need to change my address", 0, "success", ""),
    ("CALL_006", "10:05:03", 3, "transcription_completed",
     "My name is Ravi and I need to change my address", 350, "success", ""),
    ("CALL_006", "10:05:04", 4, "context_updated",
     "name=Ravi; intent=change_address", 100, "success", ""),
    ("CALL_006", "10:05:07", 5, "agent_response",
     "Could you tell me your name?", 250, "success",
     "Agent repeated a question already answered"),
    ("CALL_006", "10:05:12", 6, "call_ended",
     "", 0, "unknown", "Conversation ended after repeated question"),
]

columns = [
    "call_id",
    "timestamp",
    "event_sequence",
    "event_type",
    "transcript",
    "latency_ms",
    "status",
    "details",
]

df = pd.DataFrame(events, columns=columns)

# Convert time strings to datetime values for chronological analysis
df["timestamp"] = pd.to_datetime(
    df["timestamp"], format="%H:%M:%S"
).dt.strftime("%H:%M:%S")

# Sort events within each call
df = df.sort_values(
    ["call_id", "event_sequence"]
).reset_index(drop=True)

output_path = DATA_DIR / "voice_call_events.csv"
df.to_csv(output_path, index=False)

print("=" * 55)
print("VOICE CALL EVENT DATASET CREATED")
print("=" * 55)
print(f"Total events: {len(df)}")
print(f"Unique calls: {df['call_id'].nunique()}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path.resolve()}")

print("\nEvents per call:")
print(df.groupby("call_id").size())

print("\nEvent status counts:")
print(df["status"].value_counts())

print("\nFirst 10 events:")
print(df.head(10).to_string(index=False))
