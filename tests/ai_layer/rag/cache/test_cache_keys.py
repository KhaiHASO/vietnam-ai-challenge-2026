import pytest
from ai_layer.rag.cache.keys import build_response_cache_key, CacheKeyInput

@pytest.fixture
def cache_input():
    return CacheKeyInput(
        tenant_id="t1",
        domain_id="agriculture",
        domain_pack="d1",
        knowledge_index="i1",
        prompt_version="p1",
        policy_version="pl1",
        provider_id="fpt-ai-factory",
        model_revision="m1",
        validator_bundle="v1",
        query="Hello World",
        stateless=False,
        user_id="u1",
        session_id="s1",
        conversation_revision=1,
    )

def test_prompt_version_changes_response_cache_key(cache_input) -> None:
    original = build_response_cache_key(cache_input)
    changed = build_response_cache_key(cache_input.model_copy(update={"prompt_version": "p2"}))
    assert original != changed

def test_whitespace_normalization_yields_same_key(cache_input) -> None:
    original = build_response_cache_key(cache_input)
    changed_input = cache_input.model_copy(update={"query": " Hello   World  "})
    changed = build_response_cache_key(changed_input)
    assert original == changed


def test_user_or_conversation_revision_changes_private_response_key(cache_input) -> None:
    original = build_response_cache_key(cache_input)
    other_user = build_response_cache_key(cache_input.model_copy(update={"user_id": "u2"}))
    next_revision = build_response_cache_key(
        cache_input.model_copy(update={"conversation_revision": 2})
    )
    assert len({original, other_user, next_revision}) == 3


def test_raw_query_and_user_id_are_not_exposed_in_cache_key(cache_input) -> None:
    key = build_response_cache_key(cache_input)
    assert "Hello World" not in key
    assert "u1" not in key
