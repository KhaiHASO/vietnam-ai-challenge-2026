import os
from functools import lru_cache
from ai_layer.config import settings
from ai_layer.rag.embeddings.deterministic import DeterministicEmbeddingProvider
from ai_layer.rag.vectorstores.chroma_store import ChromaVectorStore
from ai_layer.rag.retrievers.core_retriever import CoreRetriever


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


@lru_cache(maxsize=1)
def get_vector_store():
    chroma_path = os.path.join(settings.domain_dir, ".chroma_db")
    embedding_provider = get_embedding_provider()
    return ChromaVectorStore(
        embedding_provider=embedding_provider,
        persist_directory=chroma_path,
    )


@lru_cache(maxsize=1)
def get_retriever():
    return CoreRetriever(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
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
