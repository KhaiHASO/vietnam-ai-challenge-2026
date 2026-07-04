import logging

from fastapi import HTTPException

from ai_layer.orchestrator import AIOrchestrator

logger = logging.getLogger("backend.chat")


def process_chat(query: str) -> dict[str, object]:
    try:
        orchestrator = AIOrchestrator()
        return orchestrator.process_request(query)
    except Exception:
        logger.exception("Chat orchestration failed")
        raise HTTPException(
            status_code=500,
            detail="Không thể xử lý yêu cầu chat lúc này.",
        )
