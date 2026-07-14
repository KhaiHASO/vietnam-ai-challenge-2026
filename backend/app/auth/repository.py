from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pymongo import ReturnDocument

from app.db.mongo import get_database


class AuthRepository:
    async def count_users(self) -> int:
        return await get_database().users.count_documents({})

    async def create_user(
        self,
        username: str,
        hashed_password: str,
        roles: list[str],
        tenant_id: str = "single",
        email: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        user_doc = {
            "user_id": str(uuid4()),
            "tenant_id": tenant_id,
            "username": username,
            "normalized_username": username.strip().lower(),
            "email": email,
            "hashed_password": hashed_password,
            "roles": roles,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        await get_database().users.insert_one(user_doc)
        return user_doc

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        normalized = username.strip().lower()
        return await get_database().users.find_one(
            {"$or": [{"normalized_username": normalized}, {"username": normalized}]}
        )

    async def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        return await get_database().users.find_one({"user_id": user_id})

    async def set_user_active(
        self, user_id: str, is_active: bool
    ) -> dict[str, Any] | None:
        return await get_database().users.find_one_and_update(
            {"user_id": user_id},
            {"$set": {"is_active": is_active, "updated_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )

    async def save_refresh_token(
        self,
        token_id: str,
        family_id: str,
        user_id: str,
        tenant_id: str,
        hashed_token: str,
        expires_at: datetime,
    ) -> str:
        db = get_database()
        revoked = await db.refresh_families.find_one(
            {"family_id": family_id, "revoked": True}
        )
        if revoked:
            raise ValueError("refresh token family is revoked")
        now = datetime.now(timezone.utc)
        await db.refresh_sessions.insert_one(
            {
                "token_id": token_id,
                "family_id": family_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "hashed_token": hashed_token,
                "expires_at": expires_at,
                "revoked": False,
                "consumed_at": None,
                "created_at": now,
                "updated_at": now,
            }
        )
        return token_id

    async def get_refresh_token_by_id(
        self, token_id: str
    ) -> dict[str, Any] | None:
        return await get_database().refresh_sessions.find_one({"token_id": token_id})

    async def consume_refresh_token(self, token_id: str) -> bool:
        now = datetime.now(timezone.utc)
        consumed = await get_database().refresh_sessions.find_one_and_update(
            {
                "token_id": token_id,
                "revoked": False,
                "consumed_at": None,
                "expires_at": {"$gt": now},
            },
            {"$set": {"consumed_at": now, "updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        return consumed is not None

    async def revoke_family(self, family_id: str) -> None:
        db = get_database()
        now = datetime.now(timezone.utc)
        await db.refresh_families.update_one(
            {"family_id": family_id},
            {"$set": {"revoked": True, "revoked_at": now, "updated_at": now}},
            upsert=True,
        )
        await db.refresh_sessions.update_many(
            {"family_id": family_id},
            {"$set": {"revoked": True, "revoked_at": now, "updated_at": now}},
        )

    async def is_family_revoked(self, family_id: str) -> bool:
        marker = await get_database().refresh_families.find_one(
            {"family_id": family_id, "revoked": True}
        )
        return marker is not None

    async def record_audit_event(self, event_type: str, **payload: Any) -> None:
        await get_database().audit_events.insert_one(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "occurred_at": datetime.now(timezone.utc),
                **payload,
            }
        )
