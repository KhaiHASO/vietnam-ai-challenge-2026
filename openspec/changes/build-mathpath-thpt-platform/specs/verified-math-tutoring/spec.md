## ADDED Requirements

### Requirement: Safe mathematical parsing
The math layer SHALL parse only allowlisted symbols, functions and expression structures, SHALL enforce size/complexity limits and SHALL never evaluate student text as arbitrary Python code.

#### Scenario: Parse a supported derivative expression
- **WHEN** a student submits a valid expression using configured variables and supported functions
- **THEN** the tool returns a canonical expression and explicit assumptions without executing external code

#### Scenario: Reject executable input
- **WHEN** an input contains imports, file access, attribute traversal or another disallowed construct
- **THEN** parsing returns a policy-blocked result and no execution occurs

### Requirement: Core verification operations
The math layer SHALL expose typed operations for expression normalization, equivalence, equation solving, differentiation, step checking and final-answer verification for the MVP algebra/calculus scope.

#### Scenario: Verify equivalent algebra
- **WHEN** two supported expressions are mathematically equivalent under the declared domain and assumptions
- **THEN** `check_equivalence` returns `verified` with canonical forms, tool version and evidence hash

#### Scenario: Produce a safe counterexample
- **WHEN** two expressions are not equivalent and a simple domain-valid counterexample can be produced
- **THEN** the tool returns `contradicted` with the counterexample for use in a hint

### Requirement: Domain and assumption awareness
Verification SHALL preserve variable domains, excluded values and assumptions so that simplification cannot silently change the problem.

#### Scenario: Denominator restriction is lost
- **WHEN** a transformation cancels a factor but drops an excluded denominator value
- **THEN** the step is marked contradicted or conditionally equivalent and the missing restriction is recorded

### Requirement: Bounded execution
Every math operation SHALL have deterministic complexity limits, timeout and typed error handling.

#### Scenario: Symbolic operation exceeds timeout
- **WHEN** a verification call exceeds its configured execution budget
- **THEN** it terminates and returns `timeout` without blocking the API worker or claiming the step is correct

### Requirement: Tool-required tutor conclusions
Every eligible algebra or calculus correctness conclusion shown to a student or teacher SHALL include a successful math-tool result from the same attempt context.

#### Scenario: LLM claims a step is correct without tool evidence
- **WHEN** a response draft says a supported mathematical step is correct but has no matching verified tool call
- **THEN** output validation blocks the claim and triggers bounded repair or abstention

### Requirement: Verification-aware confidence
The response confidence band SHALL be derived from verifier status, evidence quality and calibrated model signals and MUST NOT be copied from an LLM self-rating.

#### Scenario: Retrieval is strong but math verification is unsupported
- **WHEN** curriculum evidence passes but the math expression is outside tool capability
- **THEN** the response is labeled unverified/low-confidence or abstained rather than high-confidence

### Requirement: Math audit evidence
Every verification result SHALL record tool/version, normalized input hash, assumptions, status, latency and trace ID while avoiding raw sensitive identifiers.

#### Scenario: Teacher inspects a flagged step
- **WHEN** a teacher opens the evidence for a misconception
- **THEN** the system can display the relevant verification verdict and version without revealing secret configuration or chain-of-thought

