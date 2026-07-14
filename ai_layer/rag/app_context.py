import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


class AppContext:
    """
    Lightweight singleton facade for RAG dependencies.
    Providers are resolved lazily to keep module imports safe during startup.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppContext, cls).__new__(cls)
            cls._instance._resolved_dependencies: set[str] = set()
        return cls._instance

    @property
    def is_initialized(self) -> bool:
        return bool(self._resolved_dependencies)

    @property
    def embedding_provider(self):
        from ai_layer.rag.core.dependencies import get_embedding_provider

        self._resolved_dependencies.add("embedding_provider")
        return get_embedding_provider()

    @property
    def vector_store(self):
        from ai_layer.rag.core.dependencies import get_vector_store

        self._resolved_dependencies.add("vector_store")
        return get_vector_store()

    @property
    def retriever(self):
        from ai_layer.rag.core.dependencies import get_retriever

        self._resolved_dependencies.add("retriever")
        return get_retriever()

    @property
    def llm_provider(self):
        from ai_layer.rag.core.dependencies import get_llm_provider

        self._resolved_dependencies.add("llm_provider")
        return get_llm_provider()

    @property
    def rag_service(self):
        from ai_layer.rag.core.dependencies import get_rag_service

        self._resolved_dependencies.add("rag_service")
        return get_rag_service()

    def health_check(self) -> dict:
        return {
            "initialized": self.is_initialized,
            "resolved_dependencies": sorted(self._resolved_dependencies),
        }


app_context = AppContext()
