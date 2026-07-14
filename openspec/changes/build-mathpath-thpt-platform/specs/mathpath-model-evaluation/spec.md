## ADDED Requirements

### Requirement: Capability-based model registry
The system SHALL select exact model revisions by capability and domain policy rather than a single global model name or provider-specific hard-code.

#### Scenario: Select a complex tutor model
- **WHEN** a turn is classified as complex and the education policy allows external reasoning
- **THEN** the registry resolves the approved `tutor_complex` model revision and records provider/model metadata

#### Scenario: Agriculture prompt remains isolated
- **WHEN** FPT AI Factory handles an education request
- **THEN** the adapter receives the education prompt bundle and cannot inject a hard-coded agriculture system prompt

### Requirement: Reproducible model bake-off
Before a model revision is promoted, the project SHALL evaluate the same candidates on versioned MathPath math, dialogue, structured-output, safety, latency and cost cases.

#### Scenario: Promote a runtime model
- **WHEN** bake-off results are complete
- **THEN** promotion records dataset, prompt, policy, provider, exact model revision, metric values and selection rationale

### Requirement: Diagnosis release gate
The diagnosis pipeline SHALL be evaluated on at least 60 labeled cases and SHALL achieve macro-F1 `>=0.85` for the required gap/misconception outputs before claiming the target is met.

#### Scenario: F1 is below target
- **WHEN** the latest scorecard reports macro-F1 below 0.85
- **THEN** the release report marks the gate failed and does not round or hide the result

### Requirement: Mathematics accuracy release gate
The verified tutoring pipeline SHALL be evaluated on at least 80 grade 10-12 problems and SHALL achieve `>=90%` correct final feedback with tool traces for every eligible conclusion.

#### Scenario: Correct wording with wrong algebra
- **WHEN** a response is pedagogically fluent but its verified mathematical conclusion is wrong
- **THEN** the case fails mathematics accuracy regardless of LLM-judge score

### Requirement: Socratic quality release gate
The evaluation suite SHALL measure answer leakage, successful hint-chain completion and usefulness for hidden dialogues and at least ten student user tests.

#### Scenario: Evaluate the tutoring experience
- **WHEN** user-test results are aggregated
- **THEN** the gate passes only if at least 80% complete the hint chain without immediate answer leakage and mean usefulness is at least 4/5

### Requirement: Retrieval and citation evaluation
The system SHALL measure curriculum retrieval recall, reranking quality, source/citation scope and unsupported claims on teacher-labeled queries.

#### Scenario: Compare embedding and reranker candidates
- **WHEN** a candidate model is evaluated
- **THEN** the report includes recall@k, MRR or nDCG, citation precision, p95 latency and exact index/model versions

### Requirement: PyTorch baseline comparison and artifacts
The PyTorch knowledge tracer SHALL be compared with explainable rule/BKT and LLM-only baselines and SHALL produce checkpoint, config, metrics, failure cases, model card, CPU benchmark and ONNX parity artifacts.

#### Scenario: Build award evidence
- **WHEN** the approved checkpoint is exported
- **THEN** artifacts report macro-F1, high-risk recall, calibration, p95 CPU latency, throughput, model size and PyTorch-versus-ONNX output tolerance

### Requirement: Safety and privacy evaluation
The golden set SHALL include prompt injection, cross-student access, answer leakage, fixed-label bias, unsafe notification, provider failure and out-of-domain cases.

#### Scenario: Cross-student data is returned
- **WHEN** any adversarial case reveals another student's protected data
- **THEN** the safety gate fails with severity P0 and deployment is blocked

### Requirement: Latency and cost budgets
Evaluation SHALL report warm p50/p95 first-token and completion latency, tokens, estimated cost, provider fallback and cache savings by route class.

#### Scenario: Complex turn exceeds the target
- **WHEN** warm p95 completion latency for the complex path exceeds 12 seconds
- **THEN** the performance gate fails or the route is explicitly downgraded before release

### Requirement: Versioned scorecard
Every release SHALL generate a machine-readable scorecard that links code commit, domain pack, graph, index, model, prompt, policy, validator and dataset versions.

#### Scenario: Reproduce a reported metric
- **WHEN** a reviewer opens a scorecard
- **THEN** the repository provides exact commands and immutable version identifiers needed to rerun the metric

