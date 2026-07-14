from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.db.schema import COLLECTION_SPECS
from app.education.contracts import (
    AttemptEvent,
    LearnerSkillState,
    LearnerStateEvent,
)
from app.education.repository import (
    AttemptIdempotencyConflict,
    InMemoryAttemptRepository,
    InMemoryLearnerStateRepository,
    LearnerStateRevisionConflict,
)


def attempt(**updates: object) -> AttemptEvent:
    values: dict[str, object] = {
        "attempt_id": "attempt-1",
        "tenant_id": "tenant-a",
        "student_id": "student-1",
        "session_id": "session-1",
        "question_id": "question-1",
        "skill_id": "A11-CAL-07",
        "step_index": 1,
        "raw_step": "((2*x)*(x-1)-x^2)/(x-1)^2",
        "verification_status": "verified",
        "evidence": {"tool": "sympy-equivalence-v1"},
        "graph_version": "gdpt2018-v1",
        "question_version": "questions-v1",
        "policy_version": "mathpath-policy-v1",
        "model_version": "bkt-elo-v1",
        "idempotency_key": "retry-key-1",
        "created_at": datetime.now(timezone.utc),
    }
    values.update(updates)
    return AttemptEvent.model_validate(values)


def state(**updates: object) -> LearnerSkillState:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "student_id": "student-1",
        "skill_id": "A11-CAL-07",
        "mastery": 0.45,
        "confidence": 0.6,
        "evidence_count": 1,
        "recent_misconceptions": {"lost-domain-restriction": 1},
        "hint_dependency": 0.2,
        "source_attempt_ids": ("attempt-1",),
        "graph_version": "gdpt2018-v1",
        "model_version": "bkt-elo-v1",
        "revision": 0,
        "updated_at": datetime.now(timezone.utc),
    }
    values.update(updates)
    return LearnerSkillState.model_validate(values)


def test_learner_state_bounds_are_enforced() -> None:
    with pytest.raises(ValidationError):
        state(mastery=1.1)
    with pytest.raises(ValidationError):
        state(confidence=-0.1)
    with pytest.raises(ValidationError):
        state(evidence_count=-1)


@pytest.mark.asyncio
async def test_attempt_append_is_idempotent_and_tenant_scoped() -> None:
    repository = InMemoryAttemptRepository()
    original = attempt()

    first = await repository.append(original)
    replay = await repository.append(attempt(attempt_id="attempt-retry"))
    await repository.append(
        attempt(
            attempt_id="attempt-other-tenant",
            tenant_id="tenant-b",
            idempotency_key="retry-key-1",
        )
    )

    assert replay is first
    assert [item.attempt_id for item in await repository.list_for_student(
        "tenant-a", "student-1"
    )] == ["attempt-1"]
    assert [item.attempt_id for item in await repository.list_for_student(
        "tenant-b", "student-1"
    )] == ["attempt-other-tenant"]


@pytest.mark.asyncio
async def test_attempt_idempotency_key_rejects_different_payload() -> None:
    repository = InMemoryAttemptRepository()
    await repository.append(attempt())

    with pytest.raises(AttemptIdempotencyConflict):
        await repository.append(attempt(raw_step="different step"))


@pytest.mark.asyncio
async def test_learner_state_compare_and_swap_rejects_stale_revision() -> None:
    repository = InMemoryLearnerStateRepository()
    initial = await repository.save(state(), expected_revision=-1)
    accepted = initial.model_copy(
        update={
            "mastery": 0.55,
            "evidence_count": 2,
            "revision": 1,
            "source_attempt_ids": ("attempt-1", "attempt-2"),
        }
    )
    stale = accepted.model_copy(update={"mastery": 0.9})

    await repository.save(accepted, expected_revision=0)
    with pytest.raises(LearnerStateRevisionConflict):
        await repository.save(stale, expected_revision=0)

    current = await repository.get("tenant-a", "student-1", "A11-CAL-07")
    assert current is accepted
    assert current.mastery == 0.55


@pytest.mark.asyncio
async def test_learner_state_events_are_append_only_and_idempotent_by_source() -> None:
    repository = InMemoryLearnerStateRepository()
    event = LearnerStateEvent(
        event_id="state-event-1",
        tenant_id="tenant-a",
        student_id="student-1",
        skill_id="A11-CAL-07",
        event_type="verified_attempt",
        source_attempt_id="attempt-1",
        resulting_revision=0,
        payload={"correct": True},
    )

    first = await repository.append_event(event)
    replay = await repository.append_event(
        event.model_copy(update={"event_id": "state-event-retry"})
    )

    assert replay is first
    assert await repository.list_events(
        "tenant-a", "student-1", "A11-CAL-07"
    ) == [event]


def test_education_mongo_indexes_are_tenant_scoped_and_legacy_free() -> None:
    specs = {spec.name: spec for spec in COLLECTION_SPECS}
    assert {"attempt_events", "learner_state_events", "learner_state_snapshots"} <= specs.keys()
    assert not {"farms", "diagnosis_cases", "treatment_plans"} & specs.keys()

    attempt_indexes = {index.name: index for index in specs["attempt_events"].indexes}
    assert attempt_indexes["idx_attempt_events_tenant_idempotency"].keys == (
        ("tenant_id", 1),
        ("idempotency_key", 1),
    )
    assert attempt_indexes["idx_attempt_events_tenant_idempotency"].options["unique"] is True

    state_indexes = {
        index.name: index for index in specs["learner_state_snapshots"].indexes
    }
    assert state_indexes["idx_learner_state_scope"].keys == (
        ("tenant_id", 1),
        ("student_id", 1),
        ("skill_id", 1),
    )
    assert state_indexes["idx_learner_state_scope"].options["unique"] is True
