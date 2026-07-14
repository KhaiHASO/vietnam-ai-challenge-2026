import os
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

@pytest.fixture
def app(copilot_service):
    from app.main import create_app
    from app.copilot.routes import get_copilot_service
    application = create_app()
    application.dependency_overrides[get_copilot_service] = lambda: copilot_service
    return application

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def copilot_service():
    from app.copilot.service import CopilotService
    
    class MockCopilotRepository:
        def __init__(self):
            self.idempotency = {}
            self.sessions = {}
            self.messages = []
            self.events = []

        async def acquire_idempotency_key(self, key, request_hash):
            if key in self.idempotency:
                existing = self.idempotency[key]
                if existing["request_hash"] != request_hash:
                    from app.copilot.repository import IdempotencyConflict
                    raise IdempotencyConflict("Idempotency key already used with a different request hash")
                return existing
            record = {
                "idempotency_key": key,
                "request_hash": request_hash,
                "status": "pending",
                "response": None
            }
            self.idempotency[key] = record
            return None

        async def complete_idempotency_key(self, key, response):
            if key in self.idempotency:
                self.idempotency[key]["status"] = "completed"
                self.idempotency[key]["response"] = response

        async def get_session(self, session_id, user_id, tenant_id):
            return self.sessions.get(session_id)

        async def create_session(self, session_id, user_id, tenant_id, title):
            session = {
                "session_id": session_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "revision": 0,
                "title": title
            }
            self.sessions[session_id] = session
            return session

        async def append_message(self, session_id, expected_revision, message):
            session = self.sessions.get(session_id)
            if not session:
                session = await self.create_session(session_id, "u1", "t1", "")
            if session["revision"] != expected_revision:
                from app.copilot.repository import ConversationRevisionConflict
                raise ConversationRevisionConflict(f"Expected revision {expected_revision}, got {session['revision']}")
            session["revision"] += 1
            self.messages.append(message)
            return session["revision"]

        async def append_event(self, session_id, sequence, event_type, payload=None, *, event_id=None):
            event = {
                "event_id": event_id or f"event-{len(self.events)}",
                "session_id": session_id,
                "sequence": sequence,
                "type": event_type,
                "payload": payload,
            }
            self.events.append(event)
            return event["event_id"]

        async def list_events_after(self, session_id, last_event_id):
            events = [event for event in self.events if event["session_id"] == session_id]
            if last_event_id is None:
                return events
            for index, event in enumerate(events):
                if event["event_id"] == last_event_id:
                    return events[index + 1:]
            return events
            
    class MockRAGService:
        def __init__(self):
            self.calls = 0
        async def process(self, request):
            import uuid
            self.calls += 1
            from ai_layer.rag.contracts.answer import CopilotAnswer, AnswerStatus
            return CopilotAnswer(
                status=AnswerStatus.ANSWERED,
                answer="Mock response",
                message_id=str(uuid.uuid4()),
                validators_passed=True
            )

    return CopilotService(MockCopilotRepository(), MockRAGService())

@pytest.fixture
def copilot_request():
    from ai_layer.rag.contracts.request import CopilotRequest
    return CopilotRequest(
        tenant_id="t1",
        domain_id="agriculture",
        user_id="u1",
        session_id="s1",
        query="test query",
        expected_conversation_revision=0,
        idempotency_key="key-1"
    )

@pytest.fixture
def auth_header():
    from app.auth.tokens import TokenService
    from app.auth.contracts import Principal, Role
    principal = Principal(user_id="u1", tenant_id="t1", roles=frozenset([Role.OPERATOR]))
    token_service = TokenService()
    token = token_service.create_access_token(principal)
    return {"Authorization": f"Bearer {token}"}
