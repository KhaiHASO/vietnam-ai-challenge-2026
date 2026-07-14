## ADDED Requirements

### Requirement: Skill-level learner state
The system SHALL maintain learner state per student and curriculum skill with mastery, confidence, evidence count, recent misconception counts, hint dependency, timestamps and model/graph versions.

#### Scenario: First evidence for a skill
- **WHEN** a student completes their first verified attempt for a skill
- **THEN** the system creates a learner-state entry with bounded mastery/confidence values and a link to the source attempt event

### Requirement: Event-driven state updates
Learner state SHALL update only from validated attempt, hint and teacher-override events and SHALL be reproducible from the append-only event range.

#### Scenario: Valid attempt is accepted
- **WHEN** a math-verification result and question metadata pass validation
- **THEN** exactly one state update is appended and the snapshot revision advances atomically

#### Scenario: Generated tutor text is unvalidated
- **WHEN** an LLM draft fails schema, math or pedagogy validation
- **THEN** it contributes no mastery evidence and cannot change learner state

### Requirement: Explainable baseline fallback
The system SHALL provide an explainable BKT/Elo or rule baseline that can calculate mastery when the PyTorch checkpoint is absent, unhealthy or not approved.

#### Scenario: Checkpoint cannot load
- **WHEN** the active knowledge-tracing checkpoint fails integrity or compatibility checks
- **THEN** the service marks model inference degraded, uses the approved baseline and retains the failed model/version in the trace

### Requirement: Versioned PyTorch knowledge tracer
The system SHALL provide a versioned PyTorch model that consumes ordered attempt features and emits mastery, prerequisite-gap, misconception, review-risk and calibrated confidence signals.

#### Scenario: Run sequence inference
- **WHEN** sufficient recent attempts are available for a student
- **THEN** inference returns a typed signal with checkpoint version, feature schema version, latency and graph-masked candidate IDs

### Requirement: Model activation gate
A PyTorch checkpoint MUST NOT become active unless it passes schema, diagnosis quality, calibration, high-risk recall, latency and baseline-comparison gates.

#### Scenario: Candidate underperforms baseline
- **WHEN** a candidate checkpoint has lower macro-F1 than the approved baseline or violates a safety threshold
- **THEN** activation is rejected and the previous approved model remains active

### Requirement: Graph-constrained diagnosis
Predicted prerequisite gaps SHALL be constrained to the target skill's valid graph neighborhood unless an explicit out-of-graph review state is returned.

#### Scenario: Model predicts an unrelated high-logit skill
- **WHEN** the highest raw model logit is outside the allowed prerequisite neighborhood
- **THEN** the prediction is masked from automatic use and recorded only as a review signal

### Requirement: Bounded and non-stigmatizing state
Learner state SHALL describe changing skill evidence rather than permanent student ability, and stale or low-evidence signals SHALL decay or display low confidence.

#### Scenario: Teacher views a low-confidence gap
- **WHEN** a learner has too few or old attempts for a skill
- **THEN** the UI labels the signal as insufficient/low-confidence and does not present a fixed “weak student” classification

### Requirement: Concurrency-safe personalization
Practice events from multiple tabs or retries SHALL not overwrite newer learner snapshots.

#### Scenario: Revision conflict
- **WHEN** two updates target the same learner-state revision
- **THEN** one succeeds and the other reloads/recomputes from the current event sequence rather than silently losing evidence

