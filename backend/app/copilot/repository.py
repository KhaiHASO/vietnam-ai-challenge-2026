import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pymongo.errors import DuplicateKeyError
from app.db.mongo import get_database

class ConversationRevisionConflict(Exception):
    pass

class IdempotencyConflict(Exception):
    pass

class CopilotRepository:
    async def acquire_idempotency_key(self, idempotency_key: str, request_hash: str) -> dict[str, Any] | None:
        db = get_database()
        now = datetime.now(timezone.utc)
        
        try:
            record = {
                "idempotency_key": idempotency_key,
                "request_hash": request_hash,
                "status": "pending",
                "response": None,
                "created_at": now,
            }
            await db.idempotency_records.insert_one(record)
            return None # We acquired the key
        except DuplicateKeyError:
            existing = await db.idempotency_records.find_one({"idempotency_key": idempotency_key})
            if not existing:
                raise # Should not happen
            
            if existing["request_hash"] != request_hash:
                raise IdempotencyConflict("Idempotency key already used with a different request hash")
            
            return existing

    async def complete_idempotency_key(self, idempotency_key: str, response: dict[str, Any]) -> None:
        db = get_database()
        await db.idempotency_records.update_one(
            {"idempotency_key": idempotency_key},
            {"$set": {"status": "completed", "response": response}}
        )
        
    async def get_session(self, session_id: str, user_id: str, tenant_id: str) -> dict[str, Any] | None:
        return await get_database().copilot_sessions.find_one({
            "session_id": session_id,
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
    async def create_session(self, session_id: str, user_id: str, tenant_id: str, title: str = "") -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        session = {
            "session_id": session_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "revision": 0,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        await get_database().copilot_sessions.insert_one(session)
        return session
        
    async def append_message(self, session_id: str, expected_revision: int, message: dict[str, Any]) -> int:
        db = get_database()
        now = datetime.now(timezone.utc)
        
        result = await db.copilot_sessions.update_one(
            {"session_id": session_id, "revision": expected_revision},
            {"$set": {"updated_at": now, "revision": expected_revision + 1}}
        )
        
        if result.modified_count == 0:
            # Check if session exists
            session = await db.copilot_sessions.find_one({"session_id": session_id})
            if not session:
                raise ValueError("Session not found")
            raise ConversationRevisionConflict(f"Expected revision {expected_revision}, got {session['revision']}")
            
        message["session_id"] = session_id
        message["sequence"] = expected_revision + 1
        message["created_at"] = now
        await db.copilot_messages.insert_one(message)
        return expected_revision + 1
        
    async def get_messages(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        cursor = get_database().copilot_messages.find({"session_id": session_id}).sort("sequence", 1).limit(limit)
        return await cursor.to_list(length=limit)
        
    async def append_event(self, session_id: str, sequence: int, event_type: str, payload: dict[str, Any] | None = None) -> str:
        db = get_database()
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "session_id": session_id,
            "sequence": sequence,
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc)
        }
        await db.copilot_events.insert_one(event)
        return event_id
