## ADDED Requirements

### Requirement: Education MathPath domain activation
The system SHALL provide a versioned `education-mathpath` Domain Pack containing locale, prompt, policy, validator, model capability, retrieval and memory configuration, and SHALL resolve it per request without mutating a global active domain.

#### Scenario: Resolve a valid education request
- **WHEN** an authenticated request includes `domain_id=education-mathpath` and a non-empty tenant ID
- **THEN** the registry returns the exact domain, prompt, policy, validator and graph versions used for that request

#### Scenario: Reject an unknown domain
- **WHEN** a request names an unregistered domain
- **THEN** the system returns typed `OUT_OF_DOMAIN` abstention and does not fall back to agriculture

### Requirement: Minimum curriculum graph
The Domain Pack SHALL contain at least 40 active knowledge nodes across at least two THPT mathematics strands, and every node SHALL include grade, topic, Vietnamese title, learning outcomes, source references and version.

#### Scenario: Validate the graph before activation
- **WHEN** a graph revision is proposed for activation
- **THEN** validation fails unless node count, strand count, required fields, unique IDs and referenced endpoints satisfy the schema

#### Scenario: Detect invalid prerequisite cycles
- **WHEN** prerequisite edges form a cycle not explicitly allowlisted as a pedagogical review loop
- **THEN** activation fails with the involved node IDs and the previous active revision remains available

### Requirement: Provenanced curriculum relationships
Every prerequisite, part-of, similarity and remediation edge SHALL have a type, source or reviewer provenance and graph revision.

#### Scenario: Explain a prerequisite recommendation
- **WHEN** the tutor or teacher workspace reports that one skill is a prerequisite gap for another
- **THEN** the response includes the edge type, graph revision and source/reviewer reference that supports the relationship

### Requirement: Governed knowledge sources
Every RAG source SHALL record owner, usage scope, version, checksum, review status and curriculum mapping before it can be included in an active index.

#### Scenario: Reject an unreviewed source
- **WHEN** ingestion succeeds technically but the source lacks approved review status or usage scope
- **THEN** chunks remain inactive and retrieval cannot return them to students or teachers

#### Scenario: Supersede a source revision
- **WHEN** an approved newer source revision is activated
- **THEN** the index switches atomically and every subsequent answer reports the new index/source revision

### Requirement: Curriculum-aware chunking and metadata
The ingestion pipeline SHALL split curriculum outcomes, concepts, worked steps, misconceptions, questions and pedagogy policies as semantic units and SHALL attach tenant, domain, grade, strand, topic, skill, outcome, source and index metadata.

#### Scenario: Ingest a worked example
- **WHEN** a reviewed worked solution is ingested
- **THEN** each retrievable step remains associated with its problem, step order, required skill IDs, source checksum and active index revision

### Requirement: Graph-filtered hybrid retrieval
Retrieval SHALL restrict candidates to the target skill and its policy-bounded graph neighborhood before applying lexical and dense retrieval, reranking and evidence gates.

#### Scenario: Retrieve evidence for a quotient-rule error
- **WHEN** the target skill is quotient-rule differentiation and the diagnosis identifies a fraction-transformation prerequisite
- **THEN** retrieval searches the target and valid prerequisite neighborhood and excludes unrelated strands even if their text similarity is high

#### Scenario: Evidence is insufficient
- **WHEN** no reviewed source in the allowed neighborhood passes score and diversity thresholds
- **THEN** the system abstains or uses an approved non-factual hint template and does not fabricate a curriculum citation

