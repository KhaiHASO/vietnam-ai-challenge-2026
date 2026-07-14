## ADDED Requirements

### Requirement: Synthetic competition dataset
The repository SHALL provide documented synthetic data for at least 30 students, their class membership, learner histories and representative attempts without real personal data.

#### Scenario: Seed a clean environment
- **WHEN** the documented seed command runs on an empty deployment
- **THEN** it creates at least 30 pseudonymous students and all references satisfy schema and graph integrity checks

### Requirement: Five end-to-end learning journeys
The demo package SHALL define and automatically smoke-test at least five distinct learning journeys covering correct progress, prerequisite gap, repeated misconception, hint escalation and teacher intervention.

#### Scenario: Run the prerequisite-gap journey
- **WHEN** the journey seed and script execute
- **THEN** the student attempt, verification, diagnosis, hint, state update and teacher insight complete with linked trace IDs

### Requirement: Production-shaped container deployment
The project SHALL run through Docker Compose with Nginx, Next.js, FastAPI, worker, MongoDB, Redis and Chroma health/readiness checks and persistent storage.

#### Scenario: Start from a fresh clone
- **WHEN** documented environment placeholders are configured and `docker compose up --build -d` completes
- **THEN** the public URL serves the application, readiness is healthy and internal databases are not exposed publicly

### Requirement: Live deployment and rollback
The competition release SHALL have a live HTTPS URL, a pinned image/config revision and a tested rollback path to the previous working release.

#### Scenario: New release fails smoke tests
- **WHEN** post-deploy health or journey smoke tests fail
- **THEN** deployment reactivates the previous image/domain/model/index revisions without deleting durable attempt events

### Requirement: Observable demo
The system SHALL expose a safe operations view or report with route, retrieval, math-tool, model, latency, validation, abstention, fallback and cost signals for demo traces.

#### Scenario: Show a completed tutor trace
- **WHEN** an operator opens a demo turn
- **THEN** the view shows the bounded orchestration timeline and evidence/tool verdicts without secrets, PII or hidden reasoning

### Requirement: Failure-ready demo mode
The demo SHALL include bounded fallbacks for provider, LMS and network failure, and SHALL preserve a prerecorded backup of the end-to-end journey.

#### Scenario: Provider quota is exhausted during demo
- **WHEN** the primary model returns a quota or unavailable error
- **THEN** the application shows a truthful degraded/template-or-abstention path and the team can switch to a recorded backup without fake live output

### Requirement: Repository and handoff documentation
The release SHALL provide Vietnamese README, architecture, setup, seed, evaluation, demo, security/privacy, model card, LMS mapping and pilot/rollback documentation.

#### Scenario: New reviewer follows the README
- **WHEN** a reviewer with the documented prerequisites follows quick start
- **THEN** they can start the stack, log in with seeded demo roles and execute one student and one teacher journey

### Requirement: Release verification gate
The release process SHALL block the final tag if required backend/frontend tests, type checks, container smoke, schema validation, security suite or MathPath scorecard are missing or failing.

#### Scenario: Evaluation artifact is missing
- **WHEN** code tests pass but the current MathPath scorecard is absent or refers to older versions
- **THEN** release verification fails and no success claim is made

### Requirement: Pilot pathway evidence
The project SHALL document an eight-week pilot with week-by-week scope, owners, data/consent prerequisites, safety review, metrics and go/no-go criteria for up to 500 students and 20 teachers.

#### Scenario: Evaluate pilot transition
- **WHEN** the competition MVP is considered for pilot
- **THEN** transition is blocked unless accuracy gates, teacher control, privacy, traceability, incident handling and deletion/retention plans are approved

