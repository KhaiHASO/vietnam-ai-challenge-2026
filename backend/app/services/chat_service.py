import logging

from ai_layer.orchestrator import AIOrchestrator

logger = logging.getLogger("backend.chat")

RAG_FALLBACK_MESSAGE = "không đủ căn cứ"


def process_chat(query: str) -> dict[str, object]:
    try:
        orchestrator = AIOrchestrator()
        return orchestrator.process_request(query)
    except Exception as exc:
        logger.warning("Chat orchestration failed; returning RAG fallback: %s", exc.__class__.__name__)
        return {
            "success": True,
            "response": RAG_FALLBACK_MESSAGE,
            "message": RAG_FALLBACK_MESSAGE,
            "fallback_used": True,
            "fallback_reason": exc.__class__.__name__,
            "telemetry": {
                "step_4_rag": {
                    "name": "RAG / Knowledge Fallback",
                    "status": "fallback",
                    "message": RAG_FALLBACK_MESSAGE,
                }
            },
        }
