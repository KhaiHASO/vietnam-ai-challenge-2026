import os
from functools import lru_cache
from ai_layer.config import settings
from ai_layer.rag.embeddings.deterministic import DeterministicEmbeddingProvider
from ai_layer.rag.vectorstores.chroma_store import ChromaVectorStore
from ai_layer.rag.retrievers.core_retriever import CoreRetriever


def build_rag_service(*, memory=None, cache=None):
    from ai_layer.rag.service import RAGService
    from ai_layer.rag.validation.pipeline import AssurancePipeline
    from ai_layer.rag.providers.gateway import ProviderGateway
    from ai_layer.rag.providers.fpt_ai_factory import FPTAIChatAdapter
    from ai_layer.rag.agentic.graph import BoundedAgenticRunner
    from ai_layer.rag.validation.input import InputValidator
    from ai_layer.rag.validation.evidence import EvidenceValidator
    from ai_layer.rag.validation.citations import CitationValidator

    pipeline = AssurancePipeline(InputValidator(), EvidenceValidator(), CitationValidator())
    gateway = ProviderGateway(FPTAIChatAdapter())
    runner = BoundedAgenticRunner(
        retriever_factory=get_retriever,
        provider_gateway=gateway,
    )

    return RAGService(
        catalog=None,
        memory=memory,
        cache=cache,
        gateway=gateway,
        runner=runner,
        validator=pipeline,
    )


@lru_cache(maxsize=1)
def get_rag_service():
    return build_rag_service()


@lru_cache(maxsize=1)
def get_embedding_provider():
    if settings.EMBEDDING_PROVIDER == "local":
        try:
            from ai_layer.rag.embeddings.sentence_transformer import (
                SentenceTransformerSingleton,
            )

            return SentenceTransformerSingleton(model_name=settings.EMBEDDING_MODEL)
        except Exception:
            pass
    if settings.EMBEDDING_PROVIDER == "gemini":
        from ai_layer.rag.providers.gemini_embedding import GeminiEmbeddingProvider

        return GeminiEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)
    return DeterministicEmbeddingProvider()


@lru_cache(maxsize=None)
def get_vector_store(domain_id: str = "agriculture"):
    chroma_path = settings.vector_db_path_for(domain_id)
    embedding_provider = get_embedding_provider()
    return ChromaVectorStore(
        embedding_provider=embedding_provider,
        persist_directory=chroma_path,
        chroma_url=settings.CHROMA_URL,
    )


@lru_cache(maxsize=None)
def get_retriever(domain_id: str = "agriculture"):
    return CoreRetriever(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(domain_id),
        llm_provider=get_llm_provider(),
    )


@lru_cache(maxsize=1)
def get_llm_provider():
    provider = settings.PROVIDER
    if provider == "gemini":
        from ai_layer.rag.providers.gemini_llm import GeminiLLM
        api_key = settings.API_KEY or os.getenv("GEMINI_API_KEY", "")
        return GeminiLLM(api_key=api_key, model_name=settings.MODEL_NAME)
    if provider == "openai":
        from ai_layer.rag.providers.openai_llm import OpenAILLM
        return OpenAILLM(
            model_name=settings.MODEL_NAME,
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL,
        )
    from ai_layer.rag.providers.unavailable_llm import UnavailableLLMProvider
    return UnavailableLLMProvider()
