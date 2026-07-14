import pytest
from ai_layer.rag.cache.policy import CacheDecisionContext, ResponseCachePolicy
from ai_layer.rag.contracts.answer import CopilotAnswer, AnswerStatus, Abstention, AbstentionCode
from ai_layer.rag.contracts.events import ModelSignal

@pytest.fixture
def cache_policy():
    return ResponseCachePolicy()

def test_unsafe_answers_are_not_cacheable(cache_policy) -> None:
    safe_context = CacheDecisionContext(stream_completed=True, exact_scope=True)
    # High risk reason
    answer_high_risk = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="ok",
        validators_passed=True
    )
    signal_high_risk = ModelSignal(
        risk_level="high", priority=0.9, requires_review=False,
        confidence=0.9, model_version="v1", latency_ms=10, engine_status="ok"
    )
    assert cache_policy.is_eligible(answer_high_risk, [signal_high_risk], safe_context) is False

    # Abstained reason
    answer_abstained = CopilotAnswer(
        status=AnswerStatus.ABSTAINED,
        abstention=Abstention(code=AbstentionCode.OUT_OF_DOMAIN, user_message="not allowed"),
        validators_passed=True
    )
    assert cache_policy.is_eligible(answer_abstained, [], safe_context) is False

    # Valid answer
    answer_valid = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Safe answer",
        validators_passed=True
    )
    signal_safe = ModelSignal(
        risk_level="low", priority=0.2, requires_review=False,
        confidence=0.9, model_version="v1", latency_ms=10, engine_status="ok"
    )
    assert cache_policy.is_eligible(answer_valid, [signal_safe], safe_context) is True


@pytest.mark.parametrize(
    "context",
    [
        CacheDecisionContext(stream_completed=False, exact_scope=True),
        CacheDecisionContext(stream_completed=True, exact_scope=False),
        CacheDecisionContext(stream_completed=True, exact_scope=True, contains_pii=True),
        CacheDecisionContext(stream_completed=True, exact_scope=True, sensitive_context=True),
        CacheDecisionContext(stream_completed=True, exact_scope=True, provider_degraded=True),
        CacheDecisionContext(stream_completed=True, exact_scope=True, approval_required=True),
    ],
)
def test_incomplete_private_or_sensitive_answers_are_not_cacheable(cache_policy, context) -> None:
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED, answer="safe", validators_passed=True
    )
    assert cache_policy.is_eligible(answer, [], context) is False


@pytest.mark.asyncio
async def test_in_memory_cache_enforces_ttl_and_delete() -> None:
    from ai_layer.rag.cache.backend import InMemoryCacheBackend

    now = [100.0]
    cache = InMemoryCacheBackend(clock=lambda: now[0])
    await cache.set("key", "value", ttl_seconds=5)
    assert await cache.get("key") == "value"
    now[0] = 106.0
    assert await cache.get("key") is None
    await cache.set("key", "value", ttl_seconds=5)
    await cache.delete("key")
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_zero_ttl_is_never_cached() -> None:
    from ai_layer.rag.cache.backend import InMemoryCacheBackend

    cache = InMemoryCacheBackend()
    await cache.set("key", "value", ttl_seconds=0)
    assert await cache.get("key") is None
