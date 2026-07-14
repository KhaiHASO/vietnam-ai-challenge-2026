from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from ai_layer.rag.registries.curriculum_graph import load_curriculum_graph
from .seed import MathPathSeed


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class GoldenStage(_FrozenModel):
    stage_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    requirement_ids: tuple[str, ...] = Field(min_length=1)
    input: dict[str, object]
    expected_output: dict[str, object]
    expected_event_type: str = Field(min_length=1)
    visible_checkpoint: str = Field(min_length=1)


class GoldenStateTransition(_FrozenModel):
    student_id: str
    skill_id: str
    before_revision: int = Field(ge=0)
    after_revision: int = Field(ge=0)
    before_mastery: float = Field(ge=0, le=1)
    after_mastery: float = Field(ge=0, le=1)
    before_confidence: float = Field(ge=0, le=1)
    after_confidence: float = Field(ge=0, le=1)
    evidence_count_before: int = Field(ge=0)
    evidence_count_after: int = Field(ge=0)
    source_attempt_ids: tuple[str, ...] = Field(min_length=1)


class GoldenTeacherOutcome(_FrozenModel):
    insight_id: str
    draft_id: str
    final_version: str
    edit_summary: str
    approval_id: str
    approved_by: str
    approval_status: str


class GoldenLmsOutcome(_FrozenModel):
    action_type: str
    endpoint: str
    requires_approval: bool
    approval_id: str
    approval_status: str
    idempotency_key: str
    content_hash: str
    queue_status: str
    delivery_result: str


class GoldenVerticalSlice(_FrozenModel):
    fixture_version: str
    frozen_at: str
    tenant_id: str
    student_id: str
    source_seed_student_id: str
    source_seed_journey_id: str
    session_id: str
    problem_id: str
    problem_text_vi: str
    initial_expression: str
    incorrect_step: str
    corrected_step: str
    target_skill_id: str
    prerequisite_skill_id: str
    versions: dict[str, str]
    stages: tuple[GoldenStage, ...]
    state_transition: GoldenStateTransition
    teacher_outcome: GoldenTeacherOutcome
    lms_outcome: GoldenLmsOutcome


@dataclass(frozen=True)
class GoldenFixtureValidationReport:
    fixture_version: str
    stage_count: int
    requirement_count: int
    errors: tuple[str, ...]


def load_golden_fixture(path: str | Path) -> GoldenVerticalSlice:
    return GoldenVerticalSlice.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )


def validate_golden_fixture(
    fixture: GoldenVerticalSlice, *, project_root: str | Path
) -> GoldenFixtureValidationReport:
    root = Path(project_root)
    errors: list[str] = []
    orders = [stage.order for stage in fixture.stages]
    stage_ids = [stage.stage_id for stage in fixture.stages]
    requirement_ids = {
        requirement_id
        for stage in fixture.stages
        for requirement_id in stage.requirement_ids
    }

    if orders != list(range(1, len(fixture.stages) + 1)):
        errors.append("stage order must be contiguous and start at 1")
    if len(stage_ids) != len(set(stage_ids)):
        errors.append("stage IDs must be unique")
    invalid_requirements = sorted(
        requirement_id
        for requirement_id in requirement_ids
        if not requirement_id.startswith("MP-")
    )
    if invalid_requirements:
        errors.append(
            f"invalid requirement IDs: {', '.join(invalid_requirements)}"
        )

    graph = load_curriculum_graph(
        root
        / "domains"
        / "education-mathpath"
        / "knowledge"
        / "curriculum_graph.yaml"
    )
    if fixture.versions.get("graph") != graph.revision:
        errors.append("fixture graph version does not match active graph")
    prerequisite_exists = any(
        edge.edge_type == "prerequisite"
        and edge.source == fixture.prerequisite_skill_id
        and edge.target == fixture.target_skill_id
        for edge in graph.edges
    )
    if not prerequisite_exists:
        errors.append("fixture prerequisite edge is absent from active graph")

    seed = MathPathSeed.model_validate_json(
        (
            root
            / "domains"
            / "education-mathpath"
            / "data"
            / "seed_v1.json"
        ).read_text(encoding="utf-8")
    )
    if fixture.source_seed_student_id not in {
        student.student_id for student in seed.students
    }:
        errors.append("fixture source student is absent from seed")
    if fixture.source_seed_journey_id not in {
        journey.journey_id for journey in seed.journeys
    }:
        errors.append("fixture source journey is absent from seed")

    state = fixture.state_transition
    if state.student_id != fixture.student_id:
        errors.append("state transition student does not match fixture student")
    if state.skill_id != fixture.target_skill_id:
        errors.append("state transition skill does not match target skill")
    if state.after_revision != state.before_revision + 1:
        errors.append("state transition must advance exactly one revision")
    if state.evidence_count_after <= state.evidence_count_before:
        errors.append("state transition must add accepted evidence")

    if fixture.teacher_outcome.approval_status != "approved":
        errors.append("teacher outcome must be approved")
    if fixture.lms_outcome.requires_approval is not True:
        errors.append("LMS outcome must require approval")
    if fixture.lms_outcome.approval_id != fixture.teacher_outcome.approval_id:
        errors.append("LMS outcome must link the teacher approval")
    if fixture.lms_outcome.approval_status != "approved":
        errors.append("LMS action must reference an approved decision")

    return GoldenFixtureValidationReport(
        fixture_version=fixture.fixture_version,
        stage_count=len(fixture.stages),
        requirement_count=len(requirement_ids),
        errors=tuple(errors),
    )
