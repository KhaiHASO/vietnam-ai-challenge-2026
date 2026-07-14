from pathlib import Path

from app.education.golden_fixture import (
    load_golden_fixture,
    validate_golden_fixture,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    PROJECT_ROOT
    / "domains"
    / "education-mathpath"
    / "data"
    / "golden_vertical_slice.json"
)


def test_golden_vertical_slice_is_frozen_linked_and_complete() -> None:
    fixture = load_golden_fixture(FIXTURE_PATH)
    report = validate_golden_fixture(fixture, project_root=PROJECT_ROOT)

    assert report.errors == ()
    assert fixture.fixture_version == "golden-vertical-slice-v1"
    assert fixture.target_skill_id == "A11-CAL-07"
    assert fixture.prerequisite_skill_id == "A10-ALG-08"
    assert len(fixture.stages) == 9
    assert [stage.order for stage in fixture.stages] == list(range(1, 10))
    assert all(stage.requirement_ids for stage in fixture.stages)
    assert all(stage.visible_checkpoint for stage in fixture.stages)
    assert all(stage.expected_event_type for stage in fixture.stages)


def test_golden_slice_pins_versions_state_delta_and_approved_lms_outcome() -> None:
    fixture = load_golden_fixture(FIXTURE_PATH)

    assert {
        "domain_pack",
        "graph",
        "question_bank",
        "prompt",
        "policy",
        "validator",
        "runtime_model",
        "math_tool",
        "index",
    } <= fixture.versions.keys()
    assert fixture.state_transition.before_revision == 0
    assert fixture.state_transition.after_revision == 1
    assert fixture.state_transition.source_attempt_ids == (
        "ATT-GOLDEN-INCORRECT",
        "ATT-GOLDEN-CORRECTED",
    )
    assert fixture.lms_outcome.requires_approval is True
    assert fixture.lms_outcome.approval_status == "approved"
    assert fixture.lms_outcome.queue_status == "delivered"
    assert fixture.lms_outcome.idempotency_key
