
import pandas as pd
from pathlib import Path

# 1. Find the project folder and input report.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

REPORT_FILE = DATA_DIR / "call_diagnosis_report.csv"
OUTPUT_FILE = DATA_DIR / "failure_case_library.csv"

# 2. Check that the diagnosis report exists.
if not REPORT_FILE.exists():
    raise FileNotFoundError(
        f"Diagnosis report not found: {REPORT_FILE}\n"
        "Run diagnose_call_events.py first."
    )

# 3. Read the diagnoses produced in our previous stage.
diagnoses = pd.read_csv(REPORT_FILE)

# 4. Define possible recovery strategies for each diagnosis.
recovery_guidance = {
    "technical_failure": {
        "suspected_cause":
            "A connected service failed or timed out.",
        "recommended_recovery":
            "Check the service status. Retry once only if safe; "
            "otherwise verify the transaction before retrying."
    },
    "speech_recognition_mismatch": {
        "suspected_cause":
            "The recognized transcript may differ from the "
            "customer's spoken words.",
        "recommended_recovery":
            "Ask the customer to confirm the critical value "
            "before taking action."
    },
    "high_latency": {
        "suspected_cause":
            "The agent response exceeded the configured "
            "latency threshold.",
        "recommended_recovery":
            "Inspect processing and service timings to locate "
            "the delay before choosing a fix."
    },
    "stalled_processing": {
        "suspected_cause":
            "Processing remained pending without a recorded "
            "agent response.",
        "recommended_recovery":
            "Check the processing task and its timeout state. "
            "Recover safely and inform the customer if needed."
    },
    "possible_context_loss": {
        "suspected_cause":
            "The agent may not have used information already "
            "provided in the conversation.",
        "recommended_recovery":
            "Check whether conversation context was preserved "
            "and supplied to the next agent turn."
    }
}

# 5. Keep calls where our diagnosis rules detected an issue.
issues = diagnoses[
    diagnoses["investigation_status"] == "issue_detected"
].copy()

case_rows = []

# 6. Turn each diagnosed call into a case-library entry.
for index, row in issues.iterrows():
    failure_type = row["diagnosis"]

    guidance = recovery_guidance.get(
        failure_type,
        {
            "suspected_cause":
                "Cause requires further investigation.",
            "recommended_recovery":
                "Inspect the event timeline before choosing a recovery."
        }
    )

    case_rows.append({
        "case_id": f"CASE_{len(case_rows) + 1:03d}",
        "source_call_id": row["call_id"],
        "failure_type": failure_type,
        "observed_evidence": row["evidence"],
        "suspected_cause": guidance["suspected_cause"],
        "recommended_recovery": guidance["recommended_recovery"],
        "recovery_status": "not_tested",
        "validation_notes": "No recovery test has been run yet."
    })

# 7. Create a table and save it as a CSV file.
columns = [
    "case_id",
    "source_call_id",
    "failure_type",
    "observed_evidence",
    "suspected_cause",
    "recommended_recovery",
    "recovery_status",
    "validation_notes"
]

case_library = pd.DataFrame(case_rows, columns=columns)

case_library.to_csv(OUTPUT_FILE, index=False)

# 8. Display a summary so we can inspect the result.
print("\nFAILURE CASE LIBRARY CREATED")
print("=" * 50)
print(f"Cases saved: {len(case_library)}")
print(f"Output file: {OUTPUT_FILE}")

if case_library.empty:
    print("No diagnosed issues were found in the report.")
else:
    print("\nCases by failure type:")
    print(case_library["failure_type"].value_counts().to_string())

    print("\nCase library preview:")
    print(
        case_library[
            ["case_id", "source_call_id", "failure_type",
             "recovery_status"]
        ].to_string(index=False)
    )
