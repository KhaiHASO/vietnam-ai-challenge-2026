from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from app.education.contracts import AttemptEvent
from app.education.knowledge_tracing import KnowledgeTracingRuntime
from app.education.repository import (
    InMemoryLearnerStateRepository,
    LearnerStateRevisionConflict,
)
from app.education.state_update_service import LearnerStateUpdateService
from ai_layer.rag.registries.curriculum_graph import load_curriculum_graph


NOW = datetime(2026, 7, 14, 10, 0, tzinfo=timezone.utc)
HASH = "sha256:" + "a" * 64


def attempt(
    attempt_id: str,
    *,
    status: str = "verified",
    created_at: datetime = NOW,
    validation_status: str = "accepted",
    raw_step: str = "x*(x-2)/(x-1)^2, x != 1",
) -> AttemptEvent:
    return AttemptEvent(
        attempt_id=attempt_id,
        tenant_id="tenant-demo",
        student_id="STU-001",
        session_id="SESSION-001",
        question_id="Q-007",
        skill_id="A11-CAL-07",
        step_index=1,
        raw_step=raw_step,
        normalized_step="x*(x-2)/(x-1)^2",
        verification_status=status,
        evidence={
            "validation_status": validation_status,
            "math_tool": {
                "status": status,
                "tool_version": "mathpath-sympy-v1",
                "evidence_hash": HASH,
                "trace_id": f"{attempt_id}:math",
            },
            "question": {
                "skill_id": "A11-CAL-07",
                "version": "questions-v1",
                "difficulty": 0.55,
            },
            "hint_level": 0,
            "misconception_id": (
                "lost-domain-restriction" if status == "contradicted" else None
            ),
        },
        graph_version="gdpt2018-v1",
        question_version="questions-v1",
        policy_version="mathpath-policy-v1",
        model_version="fpt:qwen2.5-72b-instruct",
        idempotency_key=f"idem-{attempt_id}",
        created_at=created_at,
    )


@pytest.fixture
def repository() -> InMemoryLearnerStateRepository:
    return InMemoryLearnerStateRepository()


@pytest.fixture
def service(repository) -> LearnerStateUpdateService:
    runtime = KnowledgeTracingRuntime(
        graph=load_curriculum_graph(
            "domains/education-mathpath/knowledge/curriculum_graph.yaml"
        )
    )
    return LearnerStateUpdateService(runtime=runtime, repository=repository)


@pytest.mark.asyncio
async def test_valid_attempt_updates_snapshot_and_appends_one_source_event(
    service, repository
) -> None:
    result = await service.process_attempt(attempt("ATT-001"))

    assert result.status == "applied"
    assert result.state is not None
    assert result.state.evidence_count == 1
    assert result.state.revision == 0
    assert result.state.source_attempt_ids == ("ATT-001",)
    events = await repository.list_events(
        "tenant-demo", "STU-001", "A11-CAL-07"
    )
    assert len(events) == 1
    assert events[0].source_attempt_id == "ATT-001"
    assert events[0].payload["verification_status"] == "verified"


@pytest.mark.asyncio
async def test_unvalidated_draft_and_unbounded_verdict_never_change_state(
    service, repository
) -> None:
    draft = await service.process_attempt(
        attempt("ATT-DRAFT", validation_status="draft")
    )
    unsupported = await service.process_attempt(
        attempt("ATT-UNSUPPORTED", status="unsupported")
    )

    assert draft.status == "rejected"
    assert draft.reason_code == "attempt-not-validated"
    assert unsupported.status == "rejected"
    assert unsupported.reason_code == "non-learning-verdict"
    assert await repository.get("tenant-demo", "STU-001", "A11-CAL-07") is None
    assert await repository.list_events(
        "tenant-demo", "STU-001", "A11-CAL-07"
    ) == []


@pytest.mark.asyncio
async def test_same_attempt_retry_is_exactly_once(service, repository) -> None:
    first = await service.process_attempt(attempt("ATT-RETRY"))
    replay = await service.process_attempt(attempt("ATT-RETRY"))

    assert first.status == "applied"
    assert replay.status == "duplicate"
    state = await repository.get("tenant-demo", "STU-001", "A11-CAL-07")
    assert state is not None
    assert state.evidence_count == 1
    assert state.revision == 0
    assert len(await repository.list_events(
        "tenant-demo", "STU-001", "A11-CAL-07"
    )) == 1


@pytest.mark.asyncio
async def test_multi_tab_attempts_recompute_after_revision_conflict_without_loss(
    service, repository
) -> None:
    first, second = await asyncio.gather(
        service.process_attempt(attempt("ATT-TAB-1", created_at=NOW)),
        service.process_attempt(
            attempt(
                "ATT-TAB-2",
                status="contradicted",
                created_at=NOW + timedelta(milliseconds=1),
            )
        ),
    )

    state = await repository.get("tenant-demo", "STU-001", "A11-CAL-07")
    assert state is not None
    assert state.evidence_count == 2
    assert state.revision == 1
    assert set(state.source_attempt_ids) == {"ATT-TAB-1", "ATT-TAB-2"}
    assert len(await repository.list_events(
        "tenant-demo", "STU-001", "A11-CAL-07"
    )) == 2
    assert first.retry_count + second.retry_count >= 1


class ConflictOnceRepository(InMemoryLearnerStateRepository):
    def __init__(self) -> None:
        super().__init__()
        self.conflicts_remaining = 1

    async def commit_event(self, *args, **kwargs):
        if self.conflicts_remaining:
            self.conflicts_remaining -= 1
            raise LearnerStateRevisionConflict("forced stale revision")
        return await super().commit_event(*args, **kwargs)


@pytest.mark.asyncio
async def test_optimistic_conflict_is_reloaded_and_recomputed() -> None:
    repository = ConflictOnceRepository()
    runtime = KnowledgeTracingRuntime(
        graph=load_curriculum_graph(
            "domains/education-mathpath/knowledge/curriculum_graph.yaml"
        )
    )
    service = LearnerStateUpdateService(
        runtime=runtime, repository=repository, max_conflict_retries=2
    )

    result = await service.process_attempt(attempt("ATT-CONFLICT"))

    assert result.status == "applied"
    assert result.retry_count == 1
    assert result.state is not None
    assert result.state.evidence_count == 1


@pytest.mark.asyncio
async def test_math_tool_evidence_must_match_attempt_context(service, repository) -> None:
    bad = attempt("ATT-BAD-EVIDENCE")
    bad = bad.model_copy(
        update={
            "evidence": {
                **bad.evidence,
                "math_tool": {
                    **bad.evidence["math_tool"],
                    "trace_id": "OTHER-ATTEMPT:math",
                },
            }
        }
    )

    result = await service.process_attempt(bad)

    assert result.status == "rejected"
    assert result.reason_code == "math-evidence-attempt-mismatch"
    assert await repository.get("tenant-demo", "STU-001", "A11-CAL-07") is None
