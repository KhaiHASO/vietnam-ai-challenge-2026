from ai_layer.rag.contracts.answer import AnswerStatus, CopilotAnswer
from ai_layer.rag.evaluation.runner import (
    EvaluationCase,
    EvaluationObservation,
    GoldenSetEvaluator,
    load_golden_dataset,
)


def test_unanswerable_case_requires_abstention() -> None:
    evaluator = GoldenSetEvaluator()
    case = EvaluationCase(case_id="u1", query="Unknown", expected_abstention=True)
    answer = CopilotAnswer(status=AnswerStatus.ANSWERED, answer="fabricated", validators_passed=False)
    result = evaluator.score(case, answer)
    assert result.passed is False
    assert result.failures == ["expected_abstention"]


def test_golden_dataset_covers_required_safety_scenarios() -> None:
    categories = {case.category for case in load_golden_dataset()}

    assert {
        "answerable",
        "unanswerable",
        "conflicting",
        "injection",
        "cross_scope",
        "stale",
        "high_risk",
    }.issubset(categories)


def test_scorecard_reports_retrieval_safety_and_cost_metrics() -> None:
    evaluator = GoldenSetEvaluator()
    case = EvaluationCase(
        case_id="a1",
        query="Answerable",
        expected_evidence_chunk_ids=("chunk-1", "chunk-2"),
    )
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Grounded [1]",
        citations=[{"chunk_id": "chunk-1", "inline_reference": "[1]"}],
        validators_passed=True,
    )

    scorecard = evaluator.scorecard(
        [
            EvaluationObservation(
                case=case,
                answer=answer,
                retrieved_chunk_ids=("chunk-1", "irrelevant"),
                unsupported_claims=1,
                total_claims=4,
                policy_violations=0,
                latency_ms=120,
                input_tokens=80,
                output_tokens=20,
                cost_usd=0.002,
            )
        ]
    )

    assert scorecard.retrieval_recall_at_k == 0.5
    assert scorecard.citation_support_precision == 1.0
    assert scorecard.unsupported_claim_rate == 0.25
    assert scorecard.p95_latency_ms == 120
    assert scorecard.total_tokens == 100
