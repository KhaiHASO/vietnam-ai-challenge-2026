## ADDED Requirements

### Requirement: Teacher class authorization
Teachers SHALL access only classes and students assigned to them within the current tenant, and authorization SHALL be enforced by the backend.

#### Scenario: Teacher opens an assigned class
- **WHEN** a teacher requests insights for a class in their assignment list
- **THEN** the API returns scoped aggregate and drill-down data

#### Scenario: Teacher requests an unassigned class
- **WHEN** a teacher requests another teacher's class
- **THEN** the API returns not found or forbidden and emits an authorization audit event

### Requirement: Skill heatmap with non-color cues
The teacher dashboard SHALL present mastery/confidence by student and skill, include textual or icon cues in addition to color and expose data freshness.

#### Scenario: Heatmap cell is selected
- **WHEN** a teacher selects a low-mastery cell
- **THEN** the workspace shows mastery, confidence, evidence count, recent attempts, prerequisite context and last-updated time

### Requirement: Evidence-backed needs-support queue
The system SHALL rank students or groups needing support using bounded, versioned signals and SHALL show the factors, evidence and confidence behind each item.

#### Scenario: Student appears in the queue
- **WHEN** verified repeated misconceptions and low prerequisite mastery cross policy thresholds
- **THEN** the queue item names the affected skills and evidence factors without assigning a permanent negative label

#### Scenario: Evidence is insufficient
- **WHEN** the model signal is high but there are too few valid attempts
- **THEN** the item is marked for observation/low confidence rather than automatic intervention

### Requirement: Common misconception aggregation
The dashboard SHALL aggregate misconception counts and affected prerequisite nodes by class while preserving student-level access controls.

#### Scenario: Twelve students share an error
- **WHEN** verified attempts map twelve students to the same chain-rule misconception
- **THEN** the class view reports the count, representative de-identified evidence and linked prerequisite skills

### Requirement: Draftable intervention plan
Teachers SHALL be able to generate a draft worksheet or support plan from selected skills/groups and edit all learner-facing content before approval.

#### Scenario: Generate a 15-minute worksheet
- **WHEN** a teacher chooses a misconception group and requests a 15-minute worksheet
- **THEN** the system creates a versioned draft with questions, skill/outcome mapping, sources and rationale

### Requirement: Human approval before assignment
No intervention, negative message or assignment produced by AI SHALL be sent to students, parents or an LMS until an authorized teacher approves the final version.

#### Scenario: AI draft is created
- **WHEN** generation completes successfully
- **THEN** the draft remains pending and no outbound LMS call is made

#### Scenario: Teacher edits and approves
- **WHEN** an authorized teacher edits and approves a draft
- **THEN** the system stores the diff, actor, timestamp and evidence, then queues one idempotent outbound action

### Requirement: Teacher productivity measurement
The system SHALL instrument the defined class-summary and differentiated-assignment workflow so that baseline and assisted completion times can be compared without storing unnecessary raw content.

#### Scenario: Run the teacher timing study
- **WHEN** each of three teachers performs the agreed baseline and assisted tasks
- **THEN** the evaluation report calculates per-teacher and median time reduction and passes only at `>=50%`

### Requirement: Teacher override feedback
Teacher corrections to diagnosis, skill mapping or intervention content SHALL be stored as versioned feedback for evaluation and future model improvement, not silently overwrite audit history.

#### Scenario: Teacher changes a misconception label
- **WHEN** a teacher selects a different misconception with a reason
- **THEN** the corrected label is used in the visible workflow and an immutable feedback event links old/new values and model version

