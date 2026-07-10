import logging

from ai_layer.rag.models import CopilotRequest, CopilotAnswer
from ai_layer.rag.service import RAGService

logger = logging.getLogger("backend.chat")


async def process_legacy_chat(query: str, tenant_id: str, user_id: str, rag_service: RAGService) -> dict[str, object]:
    request = CopilotRequest(
        tenant_id=tenant_id,
        user_id=user_id,
        query=query
    )
    answer = await rag_service.process(request)
    return {
        "success": True,
        "response": answer.content,
        "message": answer.content,
        "status": answer.status.value,
        "trace": answer.trace
    }
