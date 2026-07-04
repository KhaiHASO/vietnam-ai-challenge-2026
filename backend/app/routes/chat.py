from fastapi import APIRouter

from app.schemas.common import ChatRequest
from app.services.chat_service import process_chat

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    return process_chat(request.query)
