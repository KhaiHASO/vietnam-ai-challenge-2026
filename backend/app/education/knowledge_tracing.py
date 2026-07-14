from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import math
from pathlib import Path
from typing import Iterable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field
import yaml

from ai_layer.rag.registries.curriculum_graph import CurriculumGraph

from .contracts import LearnerSkillState


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = (
    PROJECT_ROOT
    / "domains"
    / "education-mathpath"
    / "policies"
    / "knowledge-tracing.yaml"
)


class KnowledgeTracingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(min_length=1)
    active_runtime: Literal["bkt-elo-v1"]
    pytorch_runtime_enabled: Literal[False]
    initial_mastery: float = Field(gt=0, lt=1)
    bkt_guess: float = Field(gt=0, lt=1)
    bkt_slip: float = Field(gt=0, lt=1)
    bkt_learn: float = Field(gt=0, lt=1)
    bkt_weight: float = Field(ge=0, le=1)
    elo_k: float = Field(gt=0, le=1)
    hint_mastery_penalty: float = Field(ge=0, le=0.25)
    hint_dependency_alpha: float = Field(gt=0, le=1)
    confidence_evidence_scale: float = Field(gt=0)
    confidence_medium_threshold: float = Field(gt=0, lt=1)
    confidence_high_threshold: float = Field(gt=0, lt=1)
    mastery_half_life_days: float = Field(gt=0)
    confidence_half_life_days: float = Field(gt=0)
    minimum_evidence_for_diagnosis: int = Field(gt=0)
    gap_score_threshold: float = Field(ge=0, le=1)
    max_source_attempts: int = Field(gt=0)


@lru_cache(maxsize=4)
def load_knowledge_tracing_config(
    path: str | Path = DEFAULT_CONFIG_PATH,
) -> KnowledgeTracingConfig:
    return KnowledgeTracingConfig.model_validate(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


class KnowledgeTracingObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    attempt_id: str = Field(min_length=1)
    correct: bool
    hint_level: int = Field(ge=0, le=3)
    misconception_id: str | None = None
    question_difficulty: float = Field(ge=0, le=1)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


ConfidenceBand = Literal["low", "medium", "high"]


class KnowledgeTracingDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    state: LearnerSkillState
    active_runtime: Literal["bkt-elo-v1"]
    confidence_band: ConfidenceBand
    display_label: str
    explanation: dict[str, float | int | str | bool]


class ProjectedLearnerSignal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    mastery: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    confidence_band: ConfidenceBand
    age_days: float = Field(ge=0)
    source_revision: int = Field(ge=0)
    display_label: str
    active_runtime: Literal["bkt-elo-v1"]


class GraphConstrainedDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal[
        "selected",
        "insufficient_evidence",
        "out_of_graph_review",
        "no_prerequisite",
    ]
    target_skill_id: str
    selected_prerequisite_id: str | None
    allowed_prerequisite_ids: tuple[str, ...]
    masked_candidate_ids: tuple[str, ...]
    confidence: float = Field(ge=0, le=1)
    confidence_band: ConfidenceBand
    display_label: str
    graph_version: str
    active_runtime: Literal["bkt-elo-v1"]
    reason_code: str


class RuntimeSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    active_runtime: Literal["bkt-elo-v1"]
    pytorch_runtime_enabled: Literal[False]
    shadow_status: Literal["available", "degraded", "disabled"]
    shadow_model_version: str | None
    reason_code: str


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _logit(probability: float) -> float:
    bounded = _clamp(probability, 1e-6, 1 - 1e-6)
    return math.log(bounded / (1 - bounded))


def _sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


class KnowledgeTracingRuntime:
    def __init__(
        self,
        *,
        graph: CurriculumGraph,
        config: KnowledgeTracingConfig | None = None,
    ) -> None:
        self.graph = graph
        self.config = config or load_knowledge_tracing_config()
        self._node_ids = {node.id for node in graph.nodes if node.active}

    def _band(self, confidence: float) -> ConfidenceBand:
        if confidence >= self.config.confidence_high_threshold:
            return "high"
        if confidence >= self.config.confidence_medium_threshold:
            return "medium"
        return "low"

    @staticmethod
    def _display_label(band: ConfidenceBand) -> str:
        if band == "low":
            return "Tín hiệu tạm thời — cần thêm bài làm đã kiểm chứng."
        if band == "medium":
            return "Xu hướng kỹ năng đang hình thành từ bằng chứng gần đây."
        return "Ước lượng kỹ năng có độ tin cậy cao theo bằng chứng gần đây."

    def project(
        self, state: LearnerSkillState, *, as_of: datetime
    ) -> ProjectedLearnerSignal:
        age_seconds = max(0.0, (as_of - state.updated_at).total_seconds())
        age_days = age_seconds / 86_400
        mastery_factor = 0.5 ** (age_days / self.config.mastery_half_life_days)
        confidence_factor = 0.5 ** (
            age_days / self.config.confidence_half_life_days
        )
        mastery = self.config.initial_mastery + (
            state.mastery - self.config.initial_mastery
        ) * mastery_factor
        confidence = state.confidence * confidence_factor
        band = self._band(confidence)
        return ProjectedLearnerSignal(
            mastery=round(_clamp(mastery), 6),
            confidence=round(_clamp(confidence), 6),
            confidence_band=band,
            age_days=round(age_days, 6),
            source_revision=state.revision,
            display_label=self._display_label(band),
            active_runtime=self.config.active_runtime,
        )

    def update(
        self,
        state: LearnerSkillState | None,
        observation: KnowledgeTracingObservation,
        *,
        tenant_id: str,
        student_id: str,
        skill_id: str,
    ) -> KnowledgeTracingDecision:
        if skill_id not in self._node_ids:
            raise ValueError(f"unknown or inactive skill_id: {skill_id}")
        if observation.occurred_at.tzinfo is None:
            raise ValueError("observation occurred_at must be timezone-aware")
        if state is not None and (
            state.tenant_id != tenant_id
            or state.student_id != student_id
            or state.skill_id != skill_id
        ):
            raise ValueError("learner state scope mismatch")
        if state is not None and state.graph_version != self.graph.revision:
            raise ValueError("learner state graph version mismatch")
        if state is not None and state.model_version != self.config.version:
            raise ValueError("learner state model version mismatch")

        if state is None:
            prior_mastery = self.config.initial_mastery
            prior_hint_dependency = 0.0
            evidence_count = 0
            revision = -1
            misconceptions: dict[str, int] = {}
            sources: tuple[str, ...] = ()
        else:
            projected = self.project(state, as_of=observation.occurred_at)
            prior_mastery = projected.mastery
            prior_hint_dependency = state.hint_dependency
            evidence_count = state.evidence_count
            revision = state.revision
            misconceptions = dict(state.recent_misconceptions)
            sources = state.source_attempt_ids

        if observation.correct:
            numerator = prior_mastery * (1 - self.config.bkt_slip)
            denominator = numerator + (1 - prior_mastery) * self.config.bkt_guess
        else:
            numerator = prior_mastery * self.config.bkt_slip
            denominator = numerator + (1 - prior_mastery) * (
                1 - self.config.bkt_guess
            )
        bkt_posterior = numerator / denominator
        bkt_after_learning = bkt_posterior + (
            1 - bkt_posterior
        ) * self.config.bkt_learn

        difficulty_logit = _logit(observation.question_difficulty)
        elo_expected = _sigmoid(_logit(prior_mastery) - difficulty_logit)
        observed_score = 1.0 if observation.correct else 0.0
        elo_mastery = prior_mastery + self.config.elo_k * (
            observed_score - elo_expected
        )
        combined = (
            self.config.bkt_weight * bkt_after_learning
            + (1 - self.config.bkt_weight) * elo_mastery
        )
        combined -= observation.hint_level * self.config.hint_mastery_penalty
        mastery = round(_clamp(combined, 0.01, 0.99), 6)

        hint_signal = observation.hint_level / 3
        hint_dependency = (
            (1 - self.config.hint_dependency_alpha) * prior_hint_dependency
            + self.config.hint_dependency_alpha * hint_signal
        )
        new_evidence_count = evidence_count + 1
        confidence = 1 - math.exp(
            -new_evidence_count / self.config.confidence_evidence_scale
        )
        confidence *= 1 - 0.10 * hint_dependency
        confidence = round(_clamp(confidence), 6)

        if not observation.correct and observation.misconception_id:
            misconceptions[observation.misconception_id] = (
                misconceptions.get(observation.misconception_id, 0) + 1
            )
        if observation.attempt_id not in sources:
            sources = (*sources, observation.attempt_id)
        sources = sources[-self.config.max_source_attempts :]

        new_state = LearnerSkillState(
            tenant_id=tenant_id,
            student_id=student_id,
            skill_id=skill_id,
            mastery=mastery,
            confidence=confidence,
            evidence_count=new_evidence_count,
            recent_misconceptions=misconceptions,
            hint_dependency=round(_clamp(hint_dependency), 6),
            source_attempt_ids=sources,
            graph_version=self.graph.revision,
            model_version=self.config.version,
            revision=revision + 1,
            updated_at=observation.occurred_at,
        )
        band = self._band(confidence)
        return KnowledgeTracingDecision(
            state=new_state,
            active_runtime=self.config.active_runtime,
            confidence_band=band,
            display_label=self._display_label(band),
            explanation={
                "correct": observation.correct,
                "prior_mastery": round(prior_mastery, 6),
                "bkt_posterior": round(bkt_posterior, 6),
                "bkt_after_learning": round(bkt_after_learning, 6),
                "elo_expected": round(elo_expected, 6),
                "elo_mastery": round(elo_mastery, 6),
                "hint_level": observation.hint_level,
                "resulting_mastery": mastery,
                "resulting_confidence": confidence,
            },
        )

    def replay(
        self,
        observations: Iterable[KnowledgeTracingObservation],
        *,
        tenant_id: str,
        student_id: str,
        skill_id: str,
    ) -> KnowledgeTracingDecision:
        ordered = sorted(
            tuple(observations), key=lambda item: (item.occurred_at, item.attempt_id)
        )
        if not ordered:
            raise ValueError("at least one observation is required for replay")
        state: LearnerSkillState | None = None
        decision: KnowledgeTracingDecision | None = None
        for item in ordered:
            decision = self.update(
                state,
                item,
                tenant_id=tenant_id,
                student_id=student_id,
                skill_id=skill_id,
            )
            state = decision.state
        assert decision is not None
        return decision

    def _allowed_prerequisites(self, target_skill_id: str) -> tuple[str, ...]:
        if target_skill_id not in self._node_ids:
            raise ValueError(f"unknown or inactive target skill: {target_skill_id}")
        incoming: dict[str, set[str]] = {}
        for edge in self.graph.edges:
            if edge.edge_type == "prerequisite":
                incoming.setdefault(edge.target, set()).add(edge.source)
        allowed: set[str] = set()
        frontier = list(incoming.get(target_skill_id, set()))
        while frontier:
            candidate = frontier.pop()
            if candidate in allowed:
                continue
            allowed.add(candidate)
            frontier.extend(incoming.get(candidate, set()))
        return tuple(sorted(allowed))

    def diagnose_prerequisite(
        self,
        *,
        target_skill_id: str,
        candidate_gap_scores: Mapping[str, float],
        evidence_count_by_skill: Mapping[str, int],
    ) -> GraphConstrainedDiagnosis:
        allowed = self._allowed_prerequisites(target_skill_id)
        allowed_set = set(allowed)
        masked = tuple(sorted(set(candidate_gap_scores) - allowed_set))
        ranked = sorted(
            (
                (skill_id, _clamp(float(score)))
                for skill_id, score in candidate_gap_scores.items()
                if skill_id in allowed_set
            ),
            key=lambda item: (-item[1], item[0]),
        )
        eligible = [
            item for item in ranked if item[1] >= self.config.gap_score_threshold
        ]

        if not allowed:
            status = "no_prerequisite"
            reason = "target-has-no-prerequisite"
            selected = None
            confidence = 0.0
        elif not eligible:
            status = "out_of_graph_review" if masked else "insufficient_evidence"
            reason = (
                "all-candidates-masked-by-graph"
                if masked
                else "no-gap-score-above-threshold"
            )
            selected = None
            confidence = 0.0
        else:
            selected_skill, gap_score = eligible[0]
            evidence_count = max(0, evidence_count_by_skill.get(selected_skill, 0))
            evidence_confidence = 1 - math.exp(
                -evidence_count / self.config.confidence_evidence_scale
            )
            confidence = _clamp(gap_score * evidence_confidence)
            if evidence_count < self.config.minimum_evidence_for_diagnosis:
                status = "insufficient_evidence"
                reason = "prerequisite-evidence-below-minimum"
                selected = None
            else:
                status = "selected"
                reason = "graph-constrained-prerequisite-selected"
                selected = selected_skill

        confidence = round(confidence, 6)
        band = self._band(confidence)
        return GraphConstrainedDiagnosis(
            status=status,
            target_skill_id=target_skill_id,
            selected_prerequisite_id=selected,
            allowed_prerequisite_ids=allowed,
            masked_candidate_ids=masked,
            confidence=confidence,
            confidence_band=band,
            display_label=self._display_label(band),
            graph_version=self.graph.revision,
            active_runtime=self.config.active_runtime,
            reason_code=reason,
        )

    def select_active_runtime(
        self,
        *,
        shadow_checkpoint_status: str,
        shadow_model_version: str | None,
    ) -> RuntimeSelection:
        if not shadow_model_version or shadow_checkpoint_status == "disabled":
            shadow_status: Literal["available", "degraded", "disabled"] = "disabled"
            reason = "shadow-disabled"
        elif shadow_checkpoint_status == "ready":
            shadow_status = "available"
            reason = "shadow-available-baseline-remains-active"
        else:
            shadow_status = "degraded"
            reason = "shadow-unavailable-baseline-fallback"
        return RuntimeSelection(
            active_runtime=self.config.active_runtime,
            pytorch_runtime_enabled=self.config.pytorch_runtime_enabled,
            shadow_status=shadow_status,
            shadow_model_version=shadow_model_version,
            reason_code=reason,
        )
