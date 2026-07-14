## ADDED Requirements

### Requirement: Typed LMS client
The system SHALL implement a typed LMS Sandbox client for students, attempts, skills, assignments, recommendations and teacher notes, with validation independent of the education domain model.

#### Scenario: Import valid students and attempts
- **WHEN** LMS responses match the adapter contract
- **THEN** the client maps external records to pseudonymous internal IDs and validates every item before persistence

#### Scenario: LMS schema changes
- **WHEN** a response is missing required fields or contains an unsupported schema version
- **THEN** the sync run fails or quarantines the invalid records with a sanitized diagnostic and leaves the previous snapshot active

### Requirement: Minimum demonstrated endpoint coverage
The competition MVP SHALL use at least three required LMS GET endpoints and at least one approved POST endpoint in an end-to-end demo or contract test.

#### Scenario: Verify endpoint coverage
- **WHEN** the LMS integration scorecard runs
- **THEN** it fails unless students, attempts and skills or assignments have been read and a recommendation or teacher note has been posted after approval

### Requirement: Idempotent incremental synchronization
Inbound and outbound synchronization SHALL use checkpoints, external versions and idempotency keys so retries cannot duplicate attempts, assignments, recommendations or notes.

#### Scenario: Retry an outbound recommendation
- **WHEN** a network timeout occurs after the LMS accepted a recommendation
- **THEN** retrying with the same idempotency key produces one logical LMS recommendation and one internal completion record

### Requirement: Rate limit and transient failure handling
The LMS adapter SHALL respect the 120 requests/minute limit, use bounded exponential backoff for transient errors and stop retrying permanent validation/authentication failures.

#### Scenario: LMS returns 429
- **WHEN** the LMS returns a rate-limit response with or without retry metadata
- **THEN** the worker delays within the bounded retry budget and records degraded sync state

### Requirement: Degraded offline behavior
When the LMS is unavailable, the application SHALL serve the last valid local snapshot with freshness indicators and queue approved outbound actions without claiming they were delivered.

#### Scenario: Teacher approves while LMS is down
- **WHEN** a teacher approves an intervention during an outage
- **THEN** the action is queued with `pending_sync`, the UI shows that status and the worker retries later

### Requirement: LMS credential and privacy protection
LMS API keys and raw external identifiers MUST NOT appear in client-side payloads, logs or model prompts.

#### Scenario: Trace an LMS request
- **WHEN** observability captures an LMS call
- **THEN** the trace contains endpoint class, status, latency and correlation IDs but redacts authorization headers and student identifiers

### Requirement: Audited outbound changes
Every LMS write SHALL link an approved intervention, approving teacher, final content hash, idempotency key and delivery result.

#### Scenario: Post a teacher note
- **WHEN** a teacher-approved note is delivered successfully
- **THEN** audit records prove who approved it, what version was sent and which LMS response completed the action

