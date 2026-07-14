from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AttemptEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    attempt_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    step_index: int = Field(ge=0)
    raw_step: str = Field(min_length=1, max_length=4_000)
    normalized_step: str | None = Field(default=None, max_length=4_000)
    verification_status: Literal[
        "verified", "contradicted", "unsupported", "timeout"
    ]
    evidence: dict[str, object] = Field(default_factory=dict)
    graph_version: str = Field(min_length=1)
    question_version: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1, max_length=256)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnerSkillState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    mastery: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(ge=0)
    recent_misconceptions: dict[str, int] = Field(default_factory=dict)
    hint_dependency: float = Field(ge=0.0, le=1.0)
    source_attempt_ids: tuple[str, ...] = ()
    graph_version: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    revision: int = Field(ge=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnerStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    event_type: Literal["verified_attempt", "hint_used", "teacher_override"]
    source_attempt_id: str | None = None
    resulting_revision: int = Field(ge=0)
    payload: dict[str, object] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
