from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.education.knowledge_tracing import (
    KnowledgeTracingObservation,
    KnowledgeTracingRuntime,
    load_knowledge_tracing_config,
)
from ai_layer.rag.registries.curriculum_graph import load_curriculum_graph


NOW = datetime(2026, 7, 14, 9, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def runtime() -> KnowledgeTracingRuntime:
    graph = load_curriculum_graph(
        "domains/education-mathpath/knowledge/curriculum_graph.yaml"
    )
    return KnowledgeTracingRuntime(graph=graph)


def observation(
    attempt_id: str,
    *,
    correct: bool,
    day: int = 0,
    hint_level: int = 0,
    misconception_id: str | None = None,
    difficulty: float = 0.5,
) -> KnowledgeTracingObservation:
    return KnowledgeTracingObservation(
        attempt_id=attempt_id,
        correct=correct,
        hint_level=hint_level,
        misconception_id=misconception_id,
        question_difficulty=difficulty,
        occurred_at=NOW + timedelta(days=day),
    )


def test_first_evidence_creates_bounded_explainable_low_confidence_state(runtime) -> None:
    decision = runtime.update(
        None,
        observation("ATT-001", correct=True),
        tenant_id="tenant-demo",
        student_id="STU-001",
        skill_id="A11-CAL-07",
    )

    state = decision.state
    assert 0 <= state.mastery <= 1
    assert 0 <= state.confidence <= 1
    assert state.evidence_count == 1
    assert state.source_attempt_ids == ("ATT-001",)
    assert state.revision == 0
    assert state.model_version == "bkt-elo-v1"
    assert state.graph_version == "gdpt2018-v1"
    assert decision.active_runtime == "bkt-elo-v1"
    assert decision.confidence_band == "low"
    assert decision.explanation["bkt_posterior"]
    assert decision.explanation["elo_expected"]


def test_repeated_correct_evidence_increases_mastery_and_confidence(runtime) -> None:
    first = runtime.update(
        None,
        observation("ATT-001", correct=True),
        tenant_id="tenant-demo",
        student_id="STU-001",
        skill_id="A11-CAL-07",
    )
    second = runtime.update(
        first.state,
        observation("ATT-002", correct=True, day=1),
        tenant_id="tenant-demo",
        student_id="STU-001",
        skill_id="A11-CAL-07",
    )
    third = runtime.update(
        second.state,
        observation("ATT-003", correct=True, day=2),
        tenant_id="tenant-demo",
        student_id="STU-001",
        skill_id="A11-CAL-07",
    )

    assert first.state.mastery < second.state.mastery < third.state.mastery
    assert first.state.confidence < second.state.confidence < third.state.confidence
    assert third.state.revision == 2


def test_incorrect_hinted_attempt_reduces_mastery_and_records_temporary_signal(runtime) -> None:
    prior = runtime.update(
        None,
        observation("ATT-010", correct=True),
        tenant_id="tenant-demo",
        student_id="STU-002",
        skill_id="A11-CAL-07",
    )
    decision = runtime.update(
        prior.state,
        observation(
            "ATT-011",
            correct=False,
            day=1,
            hint_level=2,
            misconception_id="lost-domain-restriction",
        ),
        tenant_id="tenant-demo",
        student_id="STU-002",
        skill_id="A11-CAL-07",
    )

    assert decision.state.mastery < prior.state.mastery
    assert decision.state.recent_misconceptions == {"lost-domain-restriction": 1}
    assert decision.state.hint_dependency > 0
    assert "weak student" not in decision.display_label.lower()
    assert "học sinh yếu" not in decision.display_label.lower()


def test_replay_is_deterministic_even_when_input_events_are_out_of_order(runtime) -> None:
    observations = [
        observation("ATT-023", correct=True, day=2),
        observation("ATT-021", correct=False, day=0, misconception_id="chain-rule-omission"),
        observation("ATT-022", correct=True, day=1, hint_level=1),
    ]

    first = runtime.replay(
        observations,
        tenant_id="tenant-demo",
        student_id="STU-003",
        skill_id="A11-CAL-06",
    )
    second = runtime.replay(
        reversed(observations),
        tenant_id="tenant-demo",
        student_id="STU-003",
        skill_id="A11-CAL-06",
    )

    assert first.state == second.state
    assert first.state.source_attempt_ids == ("ATT-021", "ATT-022", "ATT-023")
    assert first.state.revision == 2


def test_stale_signal_decays_toward_prior_and_becomes_low_confidence(runtime) -> None:
    decision = runtime.replay(
        [
            observation("ATT-031", correct=True),
            observation("ATT-032", correct=True, day=1),
            observation("ATT-033", correct=True, day=2),
        ],
        tenant_id="tenant-demo",
        student_id="STU-004",
        skill_id="A11-CAL-07",
    )
    projected = runtime.project(decision.state, as_of=NOW + timedelta(days=122))

    assert projected.mastery < decision.state.mastery
    assert projected.mastery > runtime.config.initial_mastery
    assert projected.confidence < decision.state.confidence
    assert projected.confidence_band == "low"
    assert projected.source_revision == decision.state.revision
    assert "tạm thời" in projected.display_label.lower()


def test_graph_masks_unrelated_logits_and_selects_valid_prerequisite(runtime) -> None:
    diagnosis = runtime.diagnose_prerequisite(
        target_skill_id="A11-CAL-07",
        candidate_gap_scores={
            "G10-GEO-01": 0.99,
            "A10-ALG-08": 0.84,
            "A11-CAL-05": 0.72,
        },
        evidence_count_by_skill={"A10-ALG-08": 4, "A11-CAL-05": 3},
    )

    assert diagnosis.status == "selected"
    assert diagnosis.selected_prerequisite_id == "A10-ALG-08"
    assert "G10-GEO-01" in diagnosis.masked_candidate_ids
    assert diagnosis.selected_prerequisite_id in diagnosis.allowed_prerequisite_ids
    assert diagnosis.graph_version == "gdpt2018-v1"
    assert diagnosis.active_runtime == "bkt-elo-v1"


def test_only_out_of_graph_prediction_becomes_review_signal(runtime) -> None:
    diagnosis = runtime.diagnose_prerequisite(
        target_skill_id="A11-CAL-07",
        candidate_gap_scores={"G10-GEO-01": 0.99},
        evidence_count_by_skill={},
    )

    assert diagnosis.status == "out_of_graph_review"
    assert diagnosis.selected_prerequisite_id is None
    assert diagnosis.masked_candidate_ids == ("G10-GEO-01",)


def test_low_evidence_valid_gap_is_not_presented_as_fixed_label(runtime) -> None:
    diagnosis = runtime.diagnose_prerequisite(
        target_skill_id="A11-CAL-07",
        candidate_gap_scores={"A10-ALG-08": 0.91},
        evidence_count_by_skill={"A10-ALG-08": 1},
    )

    assert diagnosis.status == "insufficient_evidence"
    assert diagnosis.selected_prerequisite_id is None
    assert diagnosis.confidence_band == "low"
    assert "học sinh yếu" not in diagnosis.display_label.lower()


def test_checkpoint_failure_cannot_replace_active_baseline(runtime) -> None:
    selection = runtime.select_active_runtime(
        shadow_checkpoint_status="load_failed",
        shadow_model_version="pytorch-kt-candidate-v1",
    )

    assert selection.active_runtime == "bkt-elo-v1"
    assert selection.shadow_status == "degraded"
    assert selection.shadow_model_version == "pytorch-kt-candidate-v1"
    assert selection.pytorch_runtime_enabled is False


def test_config_keeps_baseline_active_and_pytorch_disabled() -> None:
    config = load_knowledge_tracing_config()

    assert config.version == "bkt-elo-v1"
    assert config.active_runtime == "bkt-elo-v1"
    assert config.pytorch_runtime_enabled is False
