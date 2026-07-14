"""Deterministic golden-set scoring; judge models can annotate, never override failures."""

from dataclasses import dataclass, field
import json
import math
from pathlib import Path

from ai_layer.rag.contracts.answer import AnswerStatus, CopilotAnswer


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    query: str
    category: str = "answerable"
    expected_abstention: bool = False
    min_citations: int = 0
    expected_evidence_chunk_ids: tuple[str, ...] = ()


def load_golden_dataset(path: str | Path | None = None) -> list[EvaluationCase]:
    dataset_path = Path(path) if path is not None else Path(__file__).with_name("golden_dataset.json")
    raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Golden dataset must be a list")
    return [
        EvaluationCase(
            case_id=str(item["case_id"]),
            query=str(item["query"]),
            category=str(item.get("category", "answerable")),
            expected_abstention=bool(item.get("expected_abstention", False)),
            min_citations=int(item.get("min_citations", 0)),
            expected_evidence_chunk_ids=tuple(
                str(chunk_id)
                for chunk_id in item.get("expected_evidence_chunk_ids", [])
            ),
        )
        for item in raw
    ]


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationObservation:
    """One immutable run record used for deterministic release scorecards.

    Model judges may attach commentary elsewhere, but safety, evidence and cost
    metrics here are calculated only from explicit run artefacts.
    """

    case: EvaluationCase
    answer: CopilotAnswer
    retrieved_chunk_ids: tuple[str, ...] = ()
    unsupported_claims: int = 0
    total_claims: int = 0
    policy_violations: int = 0
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@dataclass(frozen=True)
class EvaluationScorecard:
    run_count: int
    retrieval_recall_at_k: float
    citation_support_precision: float
    unsupported_claim_rate: float
    abstention_precision: float
    abstention_recall: float
    policy_violation_rate: float
    p95_latency_ms: float
    total_tokens: int
    total_cost_usd: float


class GoldenSetEvaluator:
    def score(self, case: EvaluationCase, answer: CopilotAnswer) -> EvaluationResult:
        failures: list[str] = []
        is_abstained = answer.status == AnswerStatus.ABSTAINED
        if case.expected_abstention and not is_abstained:
            failures.append("expected_abstention")
            return EvaluationResult(case_id=case.case_id, passed=False, failures=failures)
        if not case.expected_abstention and is_abstained:
            failures.append("unexpected_abstention")
        if answer.status == AnswerStatus.ANSWERED and not answer.validators_passed:
            failures.append("validators_not_passed")
        if answer.status == AnswerStatus.ANSWERED and len(answer.citations) < case.min_citations:
            failures.append("insufficient_citations")
        return EvaluationResult(case_id=case.case_id, passed=not failures, failures=failures)

    def scorecard(
        self, observations: list[EvaluationObservation]
    ) -> EvaluationScorecard:
        """Aggregate release metrics without a judge model or hidden heuristics."""
        count = len(observations)
        expected_retrieval = 0
        retrieved_expected = 0
        cited = 0
        supported_citations = 0
        unsupported_claims = 0
        total_claims = 0
        expected_abstentions = 0
        actual_abstentions = 0
        true_abstentions = 0
        policy_violations = 0
        latencies: list[float] = []
        total_tokens = 0
        total_cost = 0.0

        for observation in observations:
            case = observation.case
            answer = observation.answer
            expected_ids = set(case.expected_evidence_chunk_ids)
            retrieved_ids = set(observation.retrieved_chunk_ids)
            expected_retrieval += len(expected_ids)
            retrieved_expected += len(expected_ids & retrieved_ids)

            citation_ids = {citation.chunk_id for citation in answer.citations}
            cited += len(citation_ids)
            supported_citations += len(citation_ids & expected_ids)

            expected_abstentions += int(case.expected_abstention)
            is_abstained = answer.status == AnswerStatus.ABSTAINED
            actual_abstentions += int(is_abstained)
            true_abstentions += int(is_abstained and case.expected_abstention)

            unsupported_claims += max(0, observation.unsupported_claims)
            total_claims += max(0, observation.total_claims)
            policy_violations += max(0, observation.policy_violations)
            latencies.append(max(0.0, observation.latency_ms))
            total_tokens += max(0, observation.input_tokens) + max(
                0, observation.output_tokens
            )
            total_cost += max(0.0, observation.cost_usd)

        return EvaluationScorecard(
            run_count=count,
            retrieval_recall_at_k=_ratio(retrieved_expected, expected_retrieval),
            citation_support_precision=_ratio(supported_citations, cited),
            unsupported_claim_rate=_ratio(unsupported_claims, total_claims),
            abstention_precision=_ratio(true_abstentions, actual_abstentions),
            abstention_recall=_ratio(true_abstentions, expected_abstentions),
            policy_violation_rate=_ratio(policy_violations, count),
            p95_latency_ms=_p95(latencies),
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 8),
        )


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    # Nearest-rank gives stable, explainable p95 values for small golden sets.
    rank = max(1, math.ceil(len(values) * 0.95))
    return sorted(values)[rank - 1]
