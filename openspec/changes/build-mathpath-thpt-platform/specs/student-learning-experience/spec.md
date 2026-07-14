## ADDED Requirements

### Requirement: Student-scoped access
The system SHALL allow a student to access only their own practice sessions, attempts, learner state, history and learning path.

#### Scenario: Student opens their own path
- **WHEN** an authenticated student requests `/api/v1/education/me/learning-path`
- **THEN** the system returns only that principal's pseudonymous learner data within the current tenant

#### Scenario: Student requests another student's session
- **WHEN** a student supplies a practice or learner-state ID owned by another student
- **THEN** the system returns not found or forbidden without revealing that record's contents

### Requirement: Goal-based practice session
The student SHALL be able to start a practice session from a curriculum skill, assigned activity or recommended micro-goal, and the session SHALL pin graph, question-bank, policy and model versions.

#### Scenario: Start derivative practice
- **WHEN** a student selects “Luyện đạo hàm”
- **THEN** the system creates a session with a target skill, a diagnostic first question and version metadata rather than returning a fixed list of 20 questions

### Requirement: Step-by-step mathematical attempts
The practice UI SHALL accept short text or simple LaTeX mathematical steps, preserve step order and submit each attempt for verification and diagnosis.

#### Scenario: Submit a non-equivalent transformation
- **WHEN** a student enters a step that is not equivalent to the preceding expression
- **THEN** the UI shows a localized “cần xem lại” state, highlights the relevant region when available and does not mark the entire problem complete

#### Scenario: Network retry does not duplicate an attempt
- **WHEN** the client retries the same attempt using the same idempotency key
- **THEN** the API returns the original result and learner state is updated at most once

### Requirement: Progressive Socratic hints
The tutor SHALL use a policy-controlled hint ladder and SHALL provide at most one new instructional hint per student turn.

#### Scenario: First incorrect attempt
- **WHEN** a student's first attempt is incorrect and the learner profile does not require additional support
- **THEN** the tutor asks a short question about the applicable rule without revealing the worked step or final answer

#### Scenario: Student requests more help
- **WHEN** the student explicitly requests another hint after trying the previous hint
- **THEN** the tutor advances by one configured hint level and records the hint usage

#### Scenario: Final-answer leakage is detected
- **WHEN** a generated hint contains the final answer before policy allows it
- **THEN** output validation blocks the hint, performs at most one bounded repair and otherwise returns a safe template

### Requirement: Verified and traceable feedback
Student feedback SHALL display verification state, confidence band and the curriculum skill or prerequisite used, without exposing chain-of-thought or internal prompts.

#### Scenario: Student asks why a hint was given
- **WHEN** the student opens “Tại sao gợi ý này?”
- **THEN** the UI shows the relevant skill, prerequisite link, approved source label and math-tool verdict that supported the hint

### Requirement: Personal learning path
The system SHALL present ordered micro-goals derived from current mastery, prerequisite gaps, recent misconceptions, assignments and policy, with a human-readable reason for each recommendation.

#### Scenario: Prerequisite is below threshold
- **WHEN** the target skill depends on a prerequisite whose mastery is below the configured threshold with sufficient evidence
- **THEN** the path schedules a short prerequisite activity before returning to the target skill

### Requirement: Responsive and accessible practice
The student experience SHALL work on common mobile widths, support keyboard interaction, expose accessible labels and never rely on color alone for correctness or risk status.

#### Scenario: Mobile practice
- **WHEN** the viewport is a common phone width
- **THEN** problem, step input, tutor hint and action controls remain usable in a single column without horizontal scrolling

#### Scenario: Reduced motion
- **WHEN** the user enables reduced-motion preferences
- **THEN** instructional states remain understandable without required animation

### Requirement: Degraded learning continuity
The UI SHALL distinguish provider, LMS and verification degradation and SHALL preserve the student's work for recovery.

#### Scenario: LLM provider is unavailable
- **WHEN** the provider circuit is open during a practice turn
- **THEN** the system uses an approved graph/math-tool hint template or typed abstention, keeps the attempt and labels the response as degraded

