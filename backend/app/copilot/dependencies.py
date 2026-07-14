"""Production composition root for the RAG copilot runtime."""

from fastapi import HTTPException, Request

from app.core.config import settings
from app.db.mongo import mongo_state
from ai_layer.rag.service import RAGService


def build_runtime_rag_service(*, redis_client, database) -> RAGService:
    """Create a RAG service that cannot lose state across API instances."""
    return RAGService.build_durable(
        redis_client=redis_client,
        facts_collection=database.memory_facts,
    )


async def get_runtime_rag_service(request: Request) -> RAGService:
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None and mongo_state.connected and mongo_state.database is not None:
        return build_runtime_rag_service(
            redis_client=redis_client,
            database=mongo_state.database,
        )
    if settings.environment == "production":
        raise HTTPException(
            status_code=503,
            detail="Durable RAG dependencies are unavailable.",
        )
    return RAGService.build_default()
