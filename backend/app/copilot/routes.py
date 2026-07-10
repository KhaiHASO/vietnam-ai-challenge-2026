from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Body, HTTPException
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.auth.tokens import Principal
from app.copilot.service import CopilotService
from app.copilot.repository import CopilotRepository, ConversationRevisionConflict, IdempotencyConflict
from ai_layer.rag.service import get_rag_service, RAGService

router = APIRouter(prefix="/api/v1/copilot", tags=["Copilot"])

def get_copilot_service(rag_service: RAGService = Depends(get_rag_service)) -> CopilotService:
    repo = CopilotRepository()
    return CopilotService(repo, rag_service)

@router.post("/sessions/{session_id}/messages")
async def post_message(
    session_id: str,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    last_event_id: str | None = Header(None, alias="Last-Event-ID"),
    body: dict[str, Any] = Body(...),
    principal: Principal = Depends(get_current_user),
    service: CopilotService = Depends(get_copilot_service)
):
    try:
        generator = service.process_stream(
            session_id=session_id,
            user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            idempotency_key=idempotency_key,
            request_body=body,
            last_event_id=last_event_id
        )
        return StreamingResponse(generator, media_type="text/event-stream")
    except ConversationRevisionConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
    except IdempotencyConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
