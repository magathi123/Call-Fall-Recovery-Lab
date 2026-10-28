# AI Agent Recovery Lab
### Diagnosing AI Agent Failures and Recommending Recovery Actions

## 1. Overview

AI agents can fail in several ways during a conversation. They may respond slowly, encounter tool or service failures, or misunderstand a user's spoken input.

The **AI Agent Recovery Lab** is a prototype that explores how these failures can be diagnosed and how appropriate recovery actions can be recommended.

The project combines rule-based diagnosis, a machine learning classifier, recovery-action mapping, and scenario-based simulation to demonstrate a structured approach to improving AI agent reliability.

**Project focus:** AI Product Analytics, failure diagnosis, recovery workflows, and system evaluation.

## 2. Problem Statement

When an AI agent encounters an error, simply detecting that something went wrong is not enough. The system needs to identify the likely failure category and determine an appropriate next step.

For example:
- High latency may require investigating processing time and system state.
- A tool failure may require checking service and transaction status.
- A speech-recognition mismatch may require confirming the user's intended input.
- A conversation without detected failures may not require recovery.

This project explores how to connect failure signals to actionable recovery recommendations.

## 3. Project Objectives

- Identify common AI agent failure categories from observable signals.
- Train a Decision Tree classifier to categorize failures.
- Map predicted failure categories to recovery recommendations.
- Simulate predefined recovery success and failure scenarios.
- Evaluate classification results and verify recovery-action mappings.
- Identify limitations and areas for further validation.

## 4. System Architecture

The prototype follows this workflow:

1. **Input signals:** Collect latency, tool-failure indicators, and transcription-mismatch indicators.
2. **Failure diagnosis:** Use a Decision Tree classifier to predict a failure category.
3. **Recovery recommendation:** Map the predicted category to a predefined recovery action.
4. **Recovery simulation:** Test predefined scenarios representing successful and unsuccessful recovery conditions.
5. **Evaluation:** Compare predictions with expected diagnoses and verify action mappings.

The prototype uses synthetic training data and designed test scenarios. It does not connect to a live AI voice agent or execute real recovery operations.

## 5. Failure Categories and Recovery Actions

| Failure category | Recommended action |
|---|---|
| `no_failure` | `no_recovery_needed` |
| `high_latency` | `inspect_latency_and_processing_state` |
| `technical_failure` | `check_service_and_transaction_status` |
| `speech_mismatch` | `request_value_confirmation` |

These mappings represent the prototype's predefined recovery policy. They are recommendations, not proof that an action will resolve a real incident.

## 6. Technology Stack

- **Python** — pipeline implementation and evaluation
- **Pandas** — dataset processing and CSV reporting
- **Scikit-learn** — Decision Tree classification and evaluation metrics
- **CSV** — training data, test cases, predictions, and reports
- **VS Code** — development environment

## 7. Machine Learning Approach

The project uses a Decision Tree classifier with a maximum depth of four.

### Input features

- `latency_ms`
- `tool_failure`
- `transcription_mismatch`

### Target variable

`failure_type`

The training dataset contains 500 synthetic examples across four failure categories.

The classifier predicts the category associated with an input scenario. A separate mapping then converts the predicted category into a recovery recommendation.

Because the training labels follow predictable patterns derived from the input features, the model's performance on this dataset should not be interpreted as evidence of production-level accuracy.

## 8. Evaluation and Results

An independent scenario dataset containing 12 manually designed test cases was used to evaluate the classifier and its recovery-action mapping.

### Results

| Evaluation measure | Result |
|---|---:|
| Test scenarios | 12 |
| Correct diagnoses | 12/12 |
| Scenario diagnosis accuracy | 100% |
| Correct recovery-action mappings | 12/12 |
| End-to-end evaluation passes | 12/12 |

The end-to-end evaluation passes when both the predicted diagnosis matches the expected diagnosis and the recommended action matches the action assigned to that expected diagnosis.

### Interpretation

All 12 designed scenarios passed the defined evaluation checks. The results demonstrate consistency between the model's predictions, the expected labels, and the predefined action mapping for these test cases.

However, the test dataset is small and synthetic. It shares the same input features as the training data, and its expected labels follow a predefined diagnosis policy. The evaluation therefore does not establish generalization to real-world conversations or prove that recovery actions successfully resolve failures.

## 9. Recovery Simulation

The project also includes a recovery simulation that evaluates predefined success and failure paths for selected failure categories.

Examples include:
- Checking whether a customer confirms a corrected speech-recognition value.
- Checking whether transaction status is known after a technical failure.
- Checking whether processing completes after a latency issue.
- Checking whether conversation context is restored appropriately.

These outcomes are determined by predefined scenario conditions. They are simulated results, not observations from a production system.

## 10. Project Structure

The project includes the following scripts and data files:

```text
ai-agent-recovery-lab/
├── data/
│   ├── ml_training_dataset.csv
│   ├── independent_test_cases.csv
│   ├── independent_evaluation_results.csv
│   ├── recovery_action_evaluation.csv
│   ├── ml_recovery_recommendations_v2.csv
│   ├── ml_recovery_simulation_results_v2.csv
│   ├── ml_recovery_simulation_results_v3.csv
│   └── pipeline_evaluation_results.csv
├── recovery_simulator.py
├── train_ml_classifier.py
├── ml_recovery_integration_v2.py
├── recovery_simulator_v2.py
├── recovery_simulator_v3.py
├── evaluate_recovery_pipeline.py
├── evaluate_independent_model.py
├── evaluate_recovery_actions.py
└── README.md
```

The files listed above represent the project's documented workflow and expected outputs. Some output files are generated when their corresponding scripts run.

## 11. How to Run the Evaluation

### Prerequisites

Python and the following packages are required:

```bash
pip install pandas scikit-learn
```

### Run the independent model evaluation

From the project root:

```bash
py evaluate_independent_model.py
```

This evaluates the Decision Tree on the independent scenario dataset and saves the prediction report.

### Run the recovery-action evaluation

```bash
py evaluate_recovery_actions.py
```

This evaluates predicted diagnoses against expected diagnoses, checks recovery-action mappings, and generates:

`data/recovery_action_evaluation.csv`

## 12. Limitations

- The training data is synthetic rather than collected from real AI agent conversations.
- The independent evaluation contains only 12 designed scenarios.
- The test cases use the same input features as the training dataset.
- The current feature set does not capture the full context of a conversation.
- Recovery actions are predefined recommendations rather than executable operations.
- Simulation outcomes do not establish actual recovery success.
- The current evaluation does not measure real customer satisfaction, task completion, or production reliability.

These limitations define the next opportunities for development.

## 13. Future Improvements

1. Evaluate the model on real or carefully anonymized and manually labeled conversation logs.
2. Expand the feature set to include retry counts, tool error codes, task-completion status, and conversation context.
3. Create a richer failure taxonomy that accounts for overlapping and ambiguous failures.
4. Evaluate precision, recall, and the confusion matrix on a larger, genuinely independent dataset.
5. Track recovery outcomes using measures such as task-completion rate, repeat-failure rate, and unnecessary-recovery rate.
6. Introduce confidence thresholds and human review for uncertain predictions.
7. Integrate with a sandbox AI agent to test recovery recommendations under controlled conditions.

## 14. Key Takeaway

This project explores a practical reliability problem in AI products: connecting failure diagnosis to an actionable recovery recommendation.

Its main contribution is the integration of classification, recovery-action mapping, simulation, and evaluation into a single prototype workflow. The current results validate the defined scenarios and mapping logic; real-world performance remains to be tested.

The project demonstrates an initial approach to thinking about AI agent reliability from both a technical and a product-evaluation perspective.
