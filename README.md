# Call-Fall Recovery Lab
### Diagnosing Voice AI Failures and Designing Safer Recovery Experiences

**A prototype exploring how voice AI products can detect failures, recommend safe recovery actions, and measure whether the user can successfully complete their task.**

## 1. The Problem

Voice AI agents can fail in ways that directly affect user experience: speech may be misrecognized, tool calls may fail, responses may be delayed, or the agent may lose track of information already provided by the user.

Detecting an error is only the first step. A reliable AI product must also decide what to do next.

Should it retry? Ask the user to confirm an input? Check whether a transaction has already completed? Or hand the conversation to a human?

An inappropriate recovery can make the experience worse. For example, blindly retrying a transaction when its status is unknown could cause a duplicate action.

**Product question:** How might we help a voice AI system identify failures, choose a safe next step, and determine whether that step actually helped the user?

## 2. Project Objective

Call-Fall Recovery Lab is a Python prototype that explores a failure-to-recovery workflow for voice AI systems.

The current implementation experiments with:
- Diagnosing failures from observable signals.
- Using a Decision Tree classifier to categorize selected failure scenarios.
- Mapping predicted categories to predefined recovery recommendations.
- Simulating recovery scenarios.
- Evaluating diagnosis consistency and recovery-action mappings.

The broader product goal is to move beyond classification accuracy and understand whether failure handling improves task completion, reduces repeated failures, and protects users from unsafe recovery behavior.

## 3. How the System Works

1. **Capture signals:** Use synthetic call events containing latency, tool-failure indicators, and transcription-mismatch indicators.
2. **Diagnose:** Predict a failure category using a Decision Tree classifier.
3. **Recommend:** Map the diagnosis to a predefined recovery action.
4. **Simulate:** Evaluate selected scenarios using predefined outcome conditions.
5. **Evaluate:** Compare predictions and recommended actions against expected scenario labels.
6. **Plan product measurement:** Define the real-world outcome data needed to establish whether recovery improves user experience.

The current workflow is a prototype. It does not connect to a live voice agent, execute real recovery operations, or measure real customer outcomes.

## 4. Failure Types and Example Recovery Policies

| Failure type | Example response | Safety consideration |
|---|---|---|
| `speech_mismatch` | Confirm the misunderstood value | Avoid repeating an incorrect assumption |
| `technical_failure` | Inspect service and transaction status | Do not blindly retry an operation with unknown status |
| `high_latency` | Inspect processing state and decide whether to wait or recover | Avoid unnecessary retries while work is still running |
| `no_failure` | Continue normal interaction and monitor | Avoid unnecessary interruptions |

These are example policies, not validated production decisions. A real system would also need to consider multiple simultaneous failures, model confidence, task context, retry limits, and escalation rules.

## 5. Technical Approach

**Current technologies**
- Python
- Pandas
- Scikit-learn
- CSV-based synthetic datasets and evaluation reports

**Current model inputs**
- `latency_ms`
- `tool_failure`
- `transcription_mismatch`

**Prediction target:** `failure_type`

The repository contains a Decision Tree experiment trained on synthetic data. Its current features and labels are deliberately limited and do not represent the full complexity of real voice conversations.

A key next step is to compare the model against a transparent rules-based baseline using a documented labeling policy, noisy examples, overlapping failures, and a genuinely held-out evaluation set.

The project should not assume that machine learning is necessary: if a simpler rules-based system performs just as well and is easier to validate, that may be the better product decision.

## 6. Evaluation: What the Current Results Mean

The existing evaluation includes 12 manually designed scenarios and reports that all 12 match their expected diagnosis and recovery-action mappings.

However, the synthetic labels follow predictable rules derived from the same input signals, and the test scenarios may reproduce those rules. Therefore, the reported 100% scenario result is **not evidence of real-world model accuracy or successful recovery**.

The current evaluation is best interpreted as an initial consistency check of the defined scenarios and action mapping.

The next evaluation will compare:
- A transparent rules-based baseline.
- A Decision Tree classifier.
- Performance on overlapping and noisy failure signals.
- Failure-specific precision, recall, and confusion matrices where appropriate.
- Incorrect and unsafe recovery recommendations.
- Performance on test scenarios that were not used to define the decision policy or train the model.

Evaluation results will be reported only after these experiments are implemented and run.

## 7. Product Analytics: Metrics to Add

The following are proposed metrics for a future analytics layer. They are not yet measured on real users.

| Metric | Why it matters |
|---|---|
| Task completion rate | Did the user finish the intended task? |
| Recovery success rate | Did an attempted recovery lead to a successful task outcome? |
| Repeat-failure rate | Did the same failure happen again in the same interaction? |
| Unnecessary recovery rate | Did the system intervene when no intervention was needed? |
| Escalation rate | How often did the interaction require a human? |
| Time to task completion | Did recovery help users finish faster or introduce more delay? |

Metrics need explicit denominators and event definitions. For example, recovery success should be calculated over eligible recovery attempts with a known outcome—not inferred from a model prediction or a simulated flag.

### Proposed prioritization framework

Failure types could be prioritized using:

**Expected impact = frequency × severity × estimated cost per occurrence**

This is a proposed decision framework. Real prioritization would require reliable event volumes, outcome data, severity definitions, and cost estimates. The framework should also account for safety risks that cannot be reduced to financial cost alone.

## 8. Safety and Product Decisions

The project highlights several decisions that matter in AI product design:

- **Retry versus verify:** Check operation status before retrying an action that may have already succeeded.
- **Clarify versus assume:** Confirm uncertain speech-recognition results instead of acting on potentially incorrect values.
- **Automate versus escalate:** Use human review when the system cannot establish a safe next action.
- **Rules versus ML:** Introduce a model only when it demonstrates a measurable advantage over a simpler alternative.
- **Optimize reliability versus speed:** Reduce latency without sacrificing correctness or user trust.

These principles will guide the next iteration of the prototype.

## 9. Repository Contents

The current repository contains scripts for:
- Dataset generation and exploration.
- Failure diagnosis and model training.
- Recovery recommendation and simulation.
- Independent-scenario, action-mapping, and pipeline evaluation.
- Edge-case and scenario checks.

It also contains synthetic CSV datasets, generated reports, and a Decision Tree visualization. The repository currently includes multiple experimental script versions; consolidation into a smaller, tested package is planned.

See the repository file list for the current source of truth. The codebase structure will be updated as the refactor progresses.

## 10. Running the Existing Evaluation

Run these commands from the repository root using Python:

```powershell
py -m pip install pandas scikit-learn
py evaluate_independent_model.py
py evaluate_recovery_actions.py
```

These commands run the current scenario and recovery-action evaluations. They do not establish production model performance or real recovery success.

The scripts and their output files will be consolidated and documented as the project is refactored.

## 11. Roadmap

### Reliability and correctness
- Validate missing, malformed, and negative latency values.
- Define explicit behavior for overlapping failure signals.
- Remove sample-specific context detection.
- Standardize recovery-action names and decision rules.
- Make scripts reproducible regardless of the working directory.

### Evaluation quality
- Build a transparent rules baseline.
- Introduce realistic variation and overlapping synthetic failures.
- Document labeling rules and latency assumptions with appropriate sources.
- Add a held-out test set, failure-specific metrics, and automated tests.
- Evaluate incorrect, unnecessary, and unsafe recovery decisions.

### Product analytics
- Build a Streamlit dashboard for failure distribution and recovery outcomes.
- Rank failures by frequency, severity, and estimated impact.
- Define a metric tree connecting failure detection to task completion.
- Add SQL-based analysis if a structured event database is introduced.
- Document the event schema and data needed to evaluate a real deployment.

### Real-world validation
- Define a labeling guide for human-reviewed failure examples.
- Identify privacy and anonymization requirements for conversation logs.
- Compare offline evaluation against controlled sandbox experiments.
- Measure task outcomes before making claims about customer or business impact.

## 12. What Success Would Look Like

A stronger version of this project would demonstrate that it can:
1. Identify failure patterns without relying on sample-specific rules.
2. Recommend actions that follow explicit safety constraints.
3. Compare ML with a simpler baseline using a meaningful evaluation.
4. Explain which failure types deserve product attention and why.
5. Measure recovery outcomes rather than treating diagnosis accuracy as the final goal.

## 13. Limitations

- The data is synthetic, not collected from real customer conversations.
- The current evaluation set is small and may share the assumptions used to generate the labels.
- The current classifier uses a limited set of features and predicts one category at a time.
- Recovery outcomes are simulated rather than observed.
- No production integration, live dashboard, or real-user impact measurement is currently claimed.
- The reported scenario results do not establish generalization to real-world voice AI systems.

These limitations are part of the project scope and define the experiments needed before stronger claims can be made.

## Final Note

Call-Fall Recovery Lab is an evolving exploration of AI product reliability: connecting failure signals to safer recovery decisions and, ultimately, measurable user outcomes.

The central question is not simply whether a model can predict a failure category. It is whether the overall system can help users complete their tasks more reliably, without introducing unnecessary or unsafe actions.
