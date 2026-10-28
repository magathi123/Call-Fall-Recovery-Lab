
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
input_path = DATA_DIR / "voice_call_events.csv"
output_path = DATA_DIR / "call_diagnosis_report.csv"

df = pd.read_csv(input_path)

# These are initial, transparent diagnostic rules.
# They are not a trained AI model.
LATENCY_THRESHOLD_MS = 5000

diagnoses = []

for call_id, call in df.groupby("call_id", sort=True):
    call = call.sort_values("event_sequence")

    issues = []

    for _, event in call.iterrows():
        event_type = event["event_type"]
        status = event["status"]
        latency = event["latency_ms"]
        details = str(event["details"])
        transcript = str(event["transcript"])

        # 1. Explicitly recorded tool or event failure
        if status == "failure":
            issues.append({
                "event_sequence": event["event_sequence"],
                "timestamp": event["timestamp"],
                "category": "technical_failure",
                "evidence": details or f"{event_type} reported failure",
                "confidence": "high"
            })

        # 2. Possible speech transcription mismatch
        if "Possible amount transcription mismatch" in details:
            issues.append({
                "event_sequence": event["event_sequence"],
                "timestamp": event["timestamp"],
                "category": "speech_recognition_mismatch",
                "evidence": details,
                "confidence": "medium"
            })

        # 3. Slow processing or response
        if latency > LATENCY_THRESHOLD_MS:
            issues.append({
                "event_sequence": event["event_sequence"],
                "timestamp": event["timestamp"],
                "category": "high_latency",
                "evidence": (
                    f"{event_type} took {latency} ms; "
                    f"threshold is {LATENCY_THRESHOLD_MS} ms"
                ),
                "confidence": "high"
            })

        # 4. Possible context loss
        if "repeated a question already answered" in details:
            issues.append({
                "event_sequence": event["event_sequence"],
                "timestamp": event["timestamp"],
                "category": "possible_context_loss",
                "evidence": details,
                "confidence": "medium"
            })

    if issues:
        # The earliest flagged event in the call
        first_issue = sorted(
            issues,
            key=lambda issue: issue["event_sequence"]
        )[0]

        diagnosis = first_issue["category"]
        failure_time = first_issue["timestamp"]
        evidence = first_issue["evidence"]
        confidence = first_issue["confidence"]

        # Keep additional issues visible for investigation
        other_issues = [
            issue["category"]
            for issue in sorted(
                issues,
                key=lambda issue: issue["event_sequence"]
            )[1:]
        ]

        other_issues_text = "; ".join(other_issues)
        outcome = "issue_detected"

    else:
        diagnosis = "no_failure_detected_by_rules"
        failure_time = ""
        evidence = "No configured failure rule was triggered."
        confidence = "not_applicable"
        other_issues_text = ""
        outcome = "no_issue_flagged"

    end_events = call[call["event_type"] == "call_ended"]
    end_status = (
        end_events.iloc[-1]["status"]
        if not end_events.empty else "not_recorded"
    )
    end_details = (
        end_events.iloc[-1]["details"]
        if not end_events.empty else ""
    )

    diagnoses.append({
        "call_id": call_id,
        "diagnosis": diagnosis,
        "first_flagged_time": failure_time,
        "evidence": evidence,
        "confidence": confidence,
        "additional_flagged_issues": other_issues_text,
        "call_end_status": end_status,
        "call_end_details": end_details,
        "investigation_status": outcome
    })

report = pd.DataFrame(diagnoses)
report.to_csv(output_path, index=False)

print("=" * 65)
print("VOICE CALL FAILURE DIAGNOSIS REPORT")
print("=" * 65)

print(report.to_string(index=False))
print(f"\nReport saved to: {output_path.resolve()}")

print(
    "\nImportant: a rule-triggered issue is a diagnostic lead, "
    "not proof of the complete root cause."
)
