import json
import hashlib
from typing import Any, AsyncGenerator

from app.copilot.repository import CopilotRepository, IdempotencyConflict, ConversationRevisionConflict
from app.copilot.sse import format_sse_event
from ai_layer.rag.service import RAGService
from ai_layer.rag.contracts.request import CopilotRequest
from ai_layer.rag.contracts.answer import CopilotAnswer, AnswerStatus

class CopilotService:
    def __init__(self, repository: CopilotRepository, rag_service: RAGService):
        self.repository = repository
        self.rag = rag_service
        
    async def send(self, request: CopilotRequest) -> CopilotAnswer:
        # Check idempotency
        request_dict = request.model_dump()
        request_hash = hashlib.sha256(json.dumps(request_dict, sort_keys=True, default=str).encode()).hexdigest()
        existing_idempotency = await self.repository.acquire_idempotency_key(request.idempotency_key, request_hash)
        
        expected_revision = request.expected_conversation_revision
        
        if existing_idempotency:
            if existing_idempotency["status"] == "completed":
                response = dict(existing_idempotency["response"])
                response.pop("conversation_revision", None)
                response.pop("provider_degraded", None)
                replayed = CopilotAnswer.model_validate(response)
                replayed.validators_passed = replayed.status in {
                    AnswerStatus.ANSWERED,
                    AnswerStatus.APPROVAL_REQUIRED,
                }
                return replayed
                
        # Load session
        session = await self.repository.get_session(request.session_id, request.user_id, request.tenant_id)
        if not session:
            await self.repository.create_session(request.session_id, request.user_id, request.tenant_id, title=request.query[:50])
            
        answer = await self.rag.process(request)
        
        message = {
            "message_id": getattr(answer, "message_id", "msg-default"),
            "role": "assistant",
            "content": getattr(answer, "answer", ""),
            "status": answer.status.value,
            "trace": getattr(answer, "trace", None)
        }
        conversation_revision = await self.repository.append_message(
            request.session_id, expected_revision, message
        )
        
        response_data = answer.model_dump(mode="json")
        response_data["conversation_revision"] = conversation_revision
        response_data["provider_degraded"] = bool(
            getattr(getattr(self.rag, "gateway", None), "last_metadata", {}).get(
                "degraded", False
            )
        )
        await self.repository.complete_idempotency_key(request.idempotency_key, response_data)
        
        return answer
        
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
        start_event_id = f"evt-{sequence}-start"
        end_event_id = f"evt-{sequence}-end"
        
        if existing_idempotency:
            if existing_idempotency["status"] == "completed":
                events = await self.repository.list_events_after(session_id, last_event_id)
                if events:
                    for event in events:
                        yield format_sse_event(
                            event_id=event["event_id"],
                            event_type=event["type"],
                            payload=event.get("payload") or {},
                        )
                    return
                response = existing_idempotency["response"]
                if last_event_id != start_event_id and last_event_id != end_event_id:
                    yield format_sse_event(event_id=start_event_id, event_type="message.started", payload={"status": "retrieving"})
                if last_event_id != end_event_id:
                    final_type = "message.abstained" if response.get("status") == "abstained" else "message.completed"
                    yield format_sse_event(event_id=end_event_id, event_type=final_type, payload=response)
                return
            raise IdempotencyConflict("A request with this idempotency key is still processing")
                
        query = request_body.get("query", "")
        
        # Load session
        session = await self.repository.get_session(session_id, user_id, tenant_id)
        if not session:
            await self.repository.create_session(session_id, user_id, tenant_id, title=query[:50])
            
        copilot_request = CopilotRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            domain_id=request_body.get("domain_id") or "agriculture",
            query=query,
            expected_conversation_revision=expected_revision,
            idempotency_key=idempotency_key
        )
        
        await self.repository.append_event(
            session_id,
            sequence * 2,
            "message.started",
            {"status": "retrieving"},
            event_id=start_event_id,
        )
        if last_event_id != start_event_id:
            yield format_sse_event(event_id=start_event_id, event_type="message.started", payload={"status": "retrieving"})
        
        answer = await self.rag.process(copilot_request)
        
        message = {
            "message_id": getattr(answer, "message_id", "msg-default"),
            "role": "assistant",
            "content": getattr(answer, "answer", ""),
            "status": answer.status.value,
            "trace": getattr(answer, "trace", None)
        }
        conversation_revision = await self.repository.append_message(
            session_id, expected_revision, message
        )
        
        response_data = answer.model_dump(mode="json")
        response_data["conversation_revision"] = conversation_revision
        response_data["provider_degraded"] = bool(
            getattr(getattr(self.rag, "gateway", None), "last_metadata", {}).get(
                "degraded", False
            )
        )
        await self.repository.complete_idempotency_key(idempotency_key, response_data)
        
        if answer.status == AnswerStatus.ABSTAINED:
            event_type = "message.abstained"
        elif answer.status == AnswerStatus.APPROVAL_REQUIRED:
            event_type = "approval.required"
        else:
            event_type = "message.completed"
        await self.repository.append_event(
            session_id,
            sequence * 2 + 1,
            event_type,
            response_data,
            event_id=end_event_id,
        )
        if last_event_id != end_event_id:
            yield format_sse_event(event_id=end_event_id, event_type=event_type, payload=response_data)
