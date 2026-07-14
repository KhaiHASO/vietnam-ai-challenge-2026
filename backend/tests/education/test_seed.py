import pytest

from app.education.seed import (
    InMemorySeedStore,
    SeedPrivacyError,
    build_mathpath_seed,
    validate_mathpath_seed,
)


def test_seed_is_deterministic_complete_and_referentially_valid() -> None:
    first = build_mathpath_seed(seed=2026)
    second = build_mathpath_seed(seed=2026)
    report = validate_mathpath_seed(first)

    assert first == second
    assert report.errors == ()
    assert report.student_count >= 30
    assert report.question_count >= 10
    assert report.attempt_count >= report.student_count
    assert report.journey_count == 5
    assert {journey.kind for journey in first.journeys} == {
        "correct-progress",
        "prerequisite-gap",
        "repeated-misconception",
        "hint-escalation",
        "teacher-intervention",
    }


@pytest.mark.asyncio
async def test_seed_apply_is_idempotent() -> None:
    dataset = build_mathpath_seed(seed=2026)
    store = InMemorySeedStore()

    first = await store.apply(dataset)
    second = await store.apply(dataset)

    assert first["students"] == len(dataset.students)
    assert first["attempts"] == len(dataset.attempts)
    assert all(created == 0 for created in second.values())
    assert store.counts()["students"] == len(dataset.students)


def test_real_student_identity_fields_are_rejected() -> None:
    dataset = build_mathpath_seed(seed=2026)
    unsafe = dataset.model_copy(deep=True)
    unsafe.students[0].__dict__["email"] = "real.student@example.edu.vn"

    with pytest.raises(SeedPrivacyError, match="email"):
        validate_mathpath_seed(unsafe)


def test_broken_question_and_attempt_references_are_reported() -> None:
    dataset = build_mathpath_seed(seed=2026)
    broken = dataset.model_copy(
        update={
            "attempts": [
                dataset.attempts[0].model_copy(update={"question_id": "missing"}),
                *dataset.attempts[1:],
            ]
        }
    )

    report = validate_mathpath_seed(broken)

    assert "attempt ATT-0001 references unknown question missing" in report.errors
