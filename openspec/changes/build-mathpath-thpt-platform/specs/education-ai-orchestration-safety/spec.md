## ADDED Requirements

### Requirement: Typed bounded tutoring orchestration
The system SHALL orchestrate each tutoring turn through typed input validation, attempt observation, math verification, diagnosis, micro-goal selection, evidence retrieval, hint generation, output validation and learner-state update with bounded loops.

#### Scenario: Complete an incorrect-attempt turn
- **WHEN** a valid student attempt is mathematically contradicted
- **THEN** the orchestrator produces at most one diagnosis refresh and one response repair, emits a validated hint or abstention and records every node outcome

#### Scenario: Retry budget is exhausted
- **WHEN** retrieval or generation remains invalid after the configured bounded retry
- **THEN** the turn terminates in a typed degraded or abstained state and never loops indefinitely

### Requirement: Scoped multi-turn memory
Conversation memory SHALL be scoped by tenant, domain, user, session and revision and SHALL be used only as conversational context, not curriculum or mathematical evidence.

#### Scenario: Prior student message is loaded
- **WHEN** the next turn belongs to the same authorized session and revision chain
- **THEN** recent context can guide wording while every factual/math conclusion still requires source or tool evidence

#### Scenario: Memory from another student exists
- **WHEN** the system resolves memory for a student
- **THEN** records belonging to another student, session or tenant are not returned or included in a model prompt

### Requirement: Pedagogy and answer-leakage policy
The orchestrator SHALL enforce age-appropriate Vietnamese language, progressive hints and final-answer reveal rules independently of the LLM prompt.

#### Scenario: Model ignores the hint policy
- **WHEN** a draft gives a full worked answer at a lower hint level
- **THEN** deterministic and model-assisted policy validation blocks the draft and records an answer-leakage violation

### Requirement: Evidence and tool traceability
Every learner-facing or teacher-facing AI conclusion SHALL expose safe trace metadata for curriculum sources, math tools, model, prompt, policy, validator and graph versions.

#### Scenario: Inspect an AI conclusion
- **WHEN** an authorized user opens its evidence drawer
- **THEN** the system shows source/tool/version/verification metadata but never chain-of-thought, system prompts, secrets or raw hidden reasoning

### Requirement: Minor-data minimization
External model requests SHALL contain only the minimum pseudonymized problem, approved learner-state features and reviewed evidence needed for the turn.

#### Scenario: Build a provider payload
- **WHEN** a tutoring request is sent to an external provider
- **THEN** student name, school name, raw profile, unrelated conversation and LMS identifiers are absent

### Requirement: High-impact human control
The system MUST require durable teacher approval before any recommendation changes an official assignment, sends a negative message or creates another high-impact external action.

#### Scenario: Model proposes an at-risk intervention
- **WHEN** an orchestration result recommends targeted support for a student or group
- **THEN** the action is persisted as pending approval and no side effect executes

### Requirement: Prompt-injection separation
Retrieved documents and user content SHALL be treated as untrusted data and SHALL not alter system policy, tool permissions or authorization.

#### Scenario: Source contains malicious instruction
- **WHEN** a retrieved chunk asks the model to ignore policy or reveal data
- **THEN** the instruction is ignored/flagged, retrieval evidence can be quarantined and no unauthorized tool call occurs

### Requirement: No hidden chain-of-thought collection
The application SHALL NOT request, stream or store hidden chain-of-thought and SHALL limit traces to operational events, inputs/outputs allowed by policy and verifier/evidence results.

#### Scenario: Client subscribes to tutor events
- **WHEN** the orchestrator streams a complex turn
- **THEN** events contain status, safe rationale labels, sources, tool verdicts and timing only

### Requirement: Data lifecycle controls
Pilot mode SHALL provide configured retention, learner-data export and deletion/supersession workflows with audit; competition demo mode SHALL use synthetic data only.

#### Scenario: Delete a pilot learner profile
- **WHEN** an authorized deletion request is approved
- **THEN** personal mappings and eligible content are deleted or tombstoned across stores, indexes/caches are invalidated and an audit record remains without the deleted payload

