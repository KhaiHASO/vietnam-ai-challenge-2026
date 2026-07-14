from __future__ import annotations

import asyncio
from datetime import datetime
import re
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from .contracts import AttemptEvent, LearnerSkillState, LearnerStateEvent
from .knowledge_tracing import (
    KnowledgeTracingObservation,
    KnowledgeTracingRuntime,
)
from .repository import (
    InMemoryLearnerStateRepository,
    LearnerStateRevisionConflict,
)


_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class LearnerStateUpdateExhausted(RuntimeError):
    pass


class LearnerStateUpdateResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["applied", "duplicate", "rejected"]
    reason_code: str = Field(min_length=1)
    state: LearnerSkillState | None = None
    state_event: LearnerStateEvent | None = None
    retry_count: int = Field(ge=0)


class _ValidatedEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    question_difficulty: float = Field(ge=0, le=1)
    hint_level: int = Field(ge=0, le=3)
    misconception_id: str | None
    evidence_hash: str
    tool_version: str
    trace_id: str


class LearnerStateUpdateService:
    def __init__(
        self,
        *,
        runtime: KnowledgeTracingRuntime,
        repository: InMemoryLearnerStateRepository,
        max_conflict_retries: int = 3,
    ) -> None:
        if max_conflict_retries < 0:
            raise ValueError("max_conflict_retries must be non-negative")
        self.runtime = runtime
        self.repository = repository
        self.max_conflict_retries = max_conflict_retries

    @staticmethod
    def _mapping(value: object) -> Mapping[str, Any] | None:
        return value if isinstance(value, Mapping) else None

    def _validate_attempt(
        self, attempt: AttemptEvent
    ) -> tuple[_ValidatedEvidence | None, str | None]:
        if attempt.verification_status not in {"verified", "contradicted"}:
            return None, "non-learning-verdict"
        if attempt.graph_version != self.runtime.graph.revision:
            return None, "graph-version-mismatch"
        if attempt.evidence.get("validation_status") != "accepted":
            return None, "attempt-not-validated"

        math_tool = self._mapping(attempt.evidence.get("math_tool"))
        if math_tool is None:
            return None, "missing-math-evidence"
        if math_tool.get("status") != attempt.verification_status:
            return None, "math-evidence-status-mismatch"
        evidence_hash = math_tool.get("evidence_hash")
        if not isinstance(evidence_hash, str) or not _SHA256.fullmatch(evidence_hash):
            return None, "invalid-math-evidence-hash"
        tool_version = math_tool.get("tool_version")
        trace_id = math_tool.get("trace_id")
        if not isinstance(tool_version, str) or not tool_version:
            return None, "missing-math-tool-version"
        if not isinstance(trace_id, str) or not trace_id.startswith(
            f"{attempt.attempt_id}:"
        ):
            return None, "math-evidence-attempt-mismatch"

        question = self._mapping(attempt.evidence.get("question"))
        if question is None:
            return None, "missing-question-evidence"
        if question.get("skill_id") != attempt.skill_id:
            return None, "question-skill-mismatch"
        if question.get("version") != attempt.question_version:
            return None, "question-version-mismatch"
        difficulty = question.get("difficulty")
        if isinstance(difficulty, bool) or not isinstance(difficulty, (int, float)):
            return None, "invalid-question-difficulty"

        hint_level = attempt.evidence.get("hint_level", 0)
        if isinstance(hint_level, bool) or not isinstance(hint_level, int):
            return None, "invalid-hint-level"
        misconception = attempt.evidence.get("misconception_id")
        if misconception is not None and not isinstance(misconception, str):
            return None, "invalid-misconception-id"
        try:
            validated = _ValidatedEvidence(
                question_difficulty=float(difficulty),
                hint_level=hint_level,
                misconception_id=misconception,
                evidence_hash=evidence_hash,
                tool_version=tool_version,
                trace_id=trace_id,
            )
        except ValueError:
            return None, "invalid-learning-evidence"
        return validated, None

    async def _duplicate_result(
        self, attempt: AttemptEvent, *, retry_count: int
    ) -> LearnerStateUpdateResult | None:
        event = await self.repository.get_event_for_source(
            attempt.tenant_id,
            attempt.student_id,
            attempt.skill_id,
            "verified_attempt",
            attempt.attempt_id,
        )
        if event is None:
            return None
        state = await self.repository.get(
            attempt.tenant_id, attempt.student_id, attempt.skill_id
        )
        return LearnerStateUpdateResult(
            status="duplicate",
            reason_code="attempt-already-applied",
            state=state,
            state_event=event,
            retry_count=retry_count,
        )

    @staticmethod
    def _effective_time(attempt: AttemptEvent, state: LearnerSkillState | None) -> datetime:
        if state is None or attempt.created_at >= state.updated_at:
            return attempt.created_at
        return state.updated_at

    async def process_attempt(self, attempt: AttemptEvent) -> LearnerStateUpdateResult:
        duplicate = await self._duplicate_result(attempt, retry_count=0)
        if duplicate is not None:
            return duplicate

        evidence, rejection_reason = self._validate_attempt(attempt)
        if evidence is None:
            return LearnerStateUpdateResult(
                status="rejected",
                reason_code=rejection_reason or "attempt-validation-failed",
                retry_count=0,
            )

        for retry_count in range(self.max_conflict_retries + 1):
            duplicate = await self._duplicate_result(
                attempt, retry_count=retry_count
            )
            if duplicate is not None:
                return duplicate
            current = await self.repository.get(
                attempt.tenant_id, attempt.student_id, attempt.skill_id
            )
            expected_revision = current.revision if current else -1
            observation = KnowledgeTracingObservation(
                attempt_id=attempt.attempt_id,
                correct=attempt.verification_status == "verified",
                hint_level=evidence.hint_level,
                misconception_id=(
                    evidence.misconception_id
                    if attempt.verification_status == "contradicted"
                    else None
                ),
                question_difficulty=evidence.question_difficulty,
                occurred_at=self._effective_time(attempt, current),
            )
            decision = self.runtime.update(
                current,
                observation,
                tenant_id=attempt.tenant_id,
                student_id=attempt.student_id,
                skill_id=attempt.skill_id,
            )
            state_event = LearnerStateEvent(
                event_id=f"state:{attempt.tenant_id}:{attempt.attempt_id}",
                tenant_id=attempt.tenant_id,
                student_id=attempt.student_id,
                skill_id=attempt.skill_id,
                event_type="verified_attempt",
                source_attempt_id=attempt.attempt_id,
                resulting_revision=decision.state.revision,
                payload={
                    "verification_status": attempt.verification_status,
                    "math_evidence_hash": evidence.evidence_hash,
                    "math_tool_version": evidence.tool_version,
                    "math_trace_id": evidence.trace_id,
                    "question_id": attempt.question_id,
                    "question_version": attempt.question_version,
                    "question_difficulty": evidence.question_difficulty,
                    "hint_level": evidence.hint_level,
                    "misconception_id": evidence.misconception_id,
                    "active_runtime": decision.active_runtime,
                    "model_version": decision.state.model_version,
                    "graph_version": decision.state.graph_version,
                    "explanation": decision.explanation,
                },
                occurred_at=observation.occurred_at,
            )

            # Give concurrently accepted attempts a fair chance to race on the
            # same expected revision; the compare-and-swap below resolves it.
            await asyncio.sleep(0)
            try:
                committed_state, applied = await self.repository.commit_event(
                    decision.state,
                    state_event,
                    expected_revision=expected_revision,
                )
            except LearnerStateRevisionConflict:
                if retry_count >= self.max_conflict_retries:
                    break
                continue
            if not applied:
                duplicate_event = await self.repository.get_event_for_source(
                    attempt.tenant_id,
                    attempt.student_id,
                    attempt.skill_id,
                    "verified_attempt",
                    attempt.attempt_id,
                )
                return LearnerStateUpdateResult(
                    status="duplicate",
                    reason_code="attempt-already-applied",
                    state=committed_state,
                    state_event=duplicate_event,
                    retry_count=retry_count,
                )
            return LearnerStateUpdateResult(
                status="applied",
                reason_code="learner-state-updated",
                state=committed_state,
                state_event=state_event,
                retry_count=retry_count,
            )

        raise LearnerStateUpdateExhausted(
            f"learner-state conflict retry budget exhausted for {attempt.attempt_id}"
        )
