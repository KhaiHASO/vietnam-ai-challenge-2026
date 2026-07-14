import pytest
import asyncio
from datetime import datetime, timezone
from app.auth.tokens import TokenService
from app.auth.service import AuthService

class MockAuthRepository:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.revoked_families = set()
        self.audit_events = []
        self._rotation_lock = asyncio.Lock()

    async def get_user_by_id(self, user_id: str):
        return self.users.get(user_id)

    async def get_user_by_username(self, username: str):
        for user in self.users.values():
            if user.get("username") == username:
                return user
        return None

    async def save_refresh_token(self, token_id, family_id, user_id, tenant_id, hashed_token, expires_at):
        if family_id in self.revoked_families:
            raise ValueError("refresh token family is revoked")
        self.tokens[token_id] = {
            "token_id": token_id,
            "family_id": family_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "hashed_token": hashed_token,
            "expires_at": expires_at,
            "revoked": False,
            "consumed_at": None,
        }

    async def get_refresh_token_by_id(self, token_id: str):
        return self.tokens.get(token_id)

    async def revoke_family(self, family_id: str):
        self.revoked_families.add(family_id)
        for t in self.tokens.values():
            if t["family_id"] == family_id:
                t["revoked"] = True

    async def consume_refresh_token(self, token_id: str):
        async with self._rotation_lock:
            token = self.tokens.get(token_id)
            if not token or token["revoked"] or token["consumed_at"] is not None:
                return False
            token["consumed_at"] = datetime.now(timezone.utc)
            return True

    async def is_family_revoked(self, family_id: str):
        return family_id in self.revoked_families

    async def record_audit_event(self, event_type: str, **payload):
        self.audit_events.append({"event_type": event_type, **payload})

    async def create_user(self, username, hashed_password, roles, tenant_id="single", email=None):
        user_id = f"user-{len(self.users) + 1}"
        user = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "username": username.strip().lower(),
            "email": email,
            "hashed_password": hashed_password,
            "roles": roles,
            "is_active": True,
        }
        self.users[user_id] = user
        return user

    async def set_user_active(self, user_id: str, is_active: bool):
        user = self.users.get(user_id)
        if user:
            user["is_active"] = is_active
        return user

@pytest.fixture
def token_service():
    return TokenService()

@pytest.fixture
def auth_repository():
    repo = MockAuthRepository()
    repo.users["user1"] = {
        "user_id": "user1",
        "tenant_id": "single",
        "roles": ["operator"],
        "is_active": True,
    }
    return repo

@pytest.fixture
def auth_service(auth_repository, token_service):
    return AuthService(auth_repository, token_service)
