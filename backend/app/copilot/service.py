import json
import hashlib
from typing import Any, AsyncGenerator

from app.copilot.repository import CopilotRepository, IdempotencyConflict, ConversationRevisionConflict
from app.copilot.sse import format_sse_event
from ai_layer.rag.service import RAGService
from ai_layer.rag.models import CopilotRequest, CopilotAnswer, AnswerStatus

class CopilotService:
    def __init__(self, repository: CopilotRepository, rag_service: RAGService):
        self.repository = repository
        self.rag = rag_service
        
    async def send(self, request: CopilotRequest) -> CopilotAnswer:
        # A simple method that processes without SSE
        return await self.rag.process(request)
        
    async def process_stream(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        idempotency_key: str,
        request_body: dict[str, Any],
        last_event_id: str | None = None
    ) -> AsyncGenerator[str, None]:
        
        # Check idempotency
        request_hash = hashlib.sha256(json.dumps(request_body, sort_keys=True).encode()).hexdigest()
        existing_idempotency = await self.repository.acquire_idempotency_key(idempotency_key, request_hash)
        
        expected_revision = request_body.get("expected_conversation_revision", 0)
        sequence = expected_revision + 1
        
        if existing_idempotency:
            if existing_idempotency["status"] == "completed":
                response = existing_idempotency["response"]
                if last_event_id != "evt-2":
                    yield format_sse_event(event_id=f"evt-{sequence}-start", event_type="message.started", payload={"status": "retrieving"})
                yield format_sse_event(event_id=f"evt-{sequence}-end", event_type="message.completed", payload=response)
                return
                
        query = request_body.get("query", "")
        
        # Load session
        session = await self.repository.get_session(session_id, user_id, tenant_id)
        if not session:
            await self.repository.create_session(session_id, user_id, tenant_id, title=query[:50])
            
        copilot_request = CopilotRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            query=query
        )
        
        if last_event_id != "evt-2":
            yield format_sse_event(event_id=f"evt-{sequence}-start", event_type="message.started", payload={"status": "retrieving"})
        
        answer = await self.rag.process(copilot_request)
        
        message = {
            "message_id": answer.message_id,
            "role": "assistant",
            "content": answer.content,
            "status": answer.status.value,
            "trace": answer.trace
        }
        await self.repository.append_message(session_id, expected_revision, message)
        
        response_data = {
            "message_id": answer.message_id,
            "content": answer.content,
            "status": answer.status.value
        }
        await self.repository.complete_idempotency_key(idempotency_key, response_data)
        
        event_type = "message.abstained" if answer.status == AnswerStatus.ABSTAINED else "message.completed"
            
        yield format_sse_event(event_id=f"evt-{sequence}-end", event_type=event_type, payload=response_data)
