from ai_layer.rag.cache.backend import RedisCacheBackend
from ai_layer.rag.memory.mongo_redis_repository import MongoRedisMemoryRepository


def test_runtime_rag_composes_durable_memory_cache_and_domain_retrieval() -> None:
    from app.copilot.dependencies import build_runtime_rag_service

    class Database:
        memory_facts = object()

    service = build_runtime_rag_service(redis_client=object(), database=Database())

    assert isinstance(service.cache, RedisCacheBackend)
    assert isinstance(service.memory.repository, MongoRedisMemoryRepository)
    assert service.runner.retriever_factory is not None
