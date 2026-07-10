from fastapi import APIRouter, Depends

from app.schemas.common import ChatRequest
from app.auth.dependencies import get_current_user
from app.auth.tokens import Principal
from app.services.chat_service import process_legacy_chat
from ai_layer.rag.service import get_rag_service, RAGService

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    principal: Principal = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
) -> dict[str, object]:
    return await process_legacy_chat(request.query, principal.tenant_id, principal.user_id, rag_service)
