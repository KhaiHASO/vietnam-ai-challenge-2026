import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException

from app.auth.contracts import Principal, Role, SessionToken
from app.auth.repository import AuthRepository
from app.auth.tokens import TokenService
from app.core.config import settings
from app.core.security import hash_secret, verify_secret


class AuthService:
    def __init__(self, repository: AuthRepository, token_service: TokenService):
        self.repository = repository
        self.token_service = token_service

    @staticmethod
    def _pack_refresh_token(token_id: str, raw_secret: str) -> str:
        combined = f"{token_id}:{raw_secret}".encode()
        return base64.urlsafe_b64encode(combined).decode().rstrip("=")

    @staticmethod
    def _unpack_refresh_token(packed_token: str) -> tuple[str, str]:
        try:
            padded = packed_token + "=" * (-len(packed_token) % 4)
            token_id, raw_secret = base64.urlsafe_b64decode(padded).decode().split(":", 1)
            if not token_id or not raw_secret:
                raise ValueError
            return token_id, raw_secret
        except Exception as exc:
            raise ValueError("Invalid token format") from exc

    @staticmethod
    def _hash_refresh_token(raw_secret: str) -> str:
        return hashlib.sha256(raw_secret.encode()).hexdigest()

    async def login(self, username: str, password: str) -> SessionToken:
        user_doc = await self.repository.get_user_by_username(username.strip().lower())
        if (
            not user_doc
            or not user_doc.get("is_active")
            or not verify_secret(password, user_doc["hashed_password"])
        ):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        session = await self.issue_session(
            user_id=user_doc["user_id"],
            tenant_id=user_doc.get("tenant_id", "single"),
            roles=user_doc["roles"],
        )
        await self.repository.record_audit_event(
            "auth.login",
            user_id=user_doc["user_id"],
            tenant_id=user_doc.get("tenant_id", "single"),
        )
        return session

    async def issue_session(
        self,
        user_id: str,
        tenant_id: str,
        roles: list[str],
        family_id: str | None = None,
    ) -> SessionToken:
        principal = Principal(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=frozenset(Role(role) for role in roles),
        )
        access_token = self.token_service.create_access_token(principal)
        raw_secret = self.token_service.generate_refresh_token()
        token_id = str(uuid4())
        family_id = family_id or str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        try:
            await self.repository.save_refresh_token(
                token_id=token_id,
                family_id=family_id,
                user_id=user_id,
                tenant_id=tenant_id,
                hashed_token=self._hash_refresh_token(raw_secret),
                expires_at=expires_at,
            )
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Refresh token family is revoked") from exc

        return SessionToken(
            access_token=access_token,
            refresh_token=self._pack_refresh_token(token_id, raw_secret),
            expires_in=settings.access_token_expire_minutes * 60,
            family_id=family_id,
        )

    async def rotate_refresh(self, refresh_token: str) -> SessionToken:
        try:
            token_id, raw_secret = self._unpack_refresh_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

        token_doc = await self.repository.get_refresh_token_by_id(token_id)
        if not token_doc or not secrets.compare_digest(
            self._hash_refresh_token(raw_secret), token_doc.get("hashed_token", "")
        ):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        family_id = token_doc["family_id"]
        if token_doc.get("revoked") or token_doc.get("consumed_at") is not None:
            await self._revoke_reused_family(family_id, token_doc["user_id"])

        expires_at = token_doc["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if datetime.now(timezone.utc) >= expires_at:
            raise HTTPException(status_code=401, detail="Refresh token expired")

        if not await self.repository.consume_refresh_token(token_id):
            await self._revoke_reused_family(family_id, token_doc["user_id"])

        user_doc = await self.repository.get_user_by_id(token_doc["user_id"])
        if not user_doc or not user_doc.get("is_active"):
            await self.repository.revoke_family(family_id)
            raise HTTPException(status_code=401, detail="User is inactive or deleted")

        session = await self.issue_session(
            user_id=user_doc["user_id"],
            tenant_id=user_doc.get("tenant_id", token_doc.get("tenant_id", "single")),
            roles=user_doc["roles"],
            family_id=family_id,
        )
        await self.repository.record_audit_event(
            "auth.refresh_rotated",
            user_id=user_doc["user_id"],
            tenant_id=user_doc.get("tenant_id", "single"),
            family_id=family_id,
        )
        return session

    async def _revoke_reused_family(self, family_id: str, user_id: str) -> None:
        await self.repository.revoke_family(family_id)
        await self.repository.record_audit_event(
            "auth.refresh_reuse", user_id=user_id, family_id=family_id
        )
        raise HTTPException(
            status_code=401,
            detail="Refresh token reuse detected. Family revoked.",
        )

    async def logout(self, refresh_token: str) -> None:
        try:
            token_id, raw_secret = self._unpack_refresh_token(refresh_token)
        except ValueError:
            return
        token_doc = await self.repository.get_refresh_token_by_id(token_id)
        if token_doc and secrets.compare_digest(
            self._hash_refresh_token(raw_secret), token_doc.get("hashed_token", "")
        ):
            await self.repository.revoke_family(token_doc["family_id"])
            await self.repository.record_audit_event(
                "auth.logout",
                user_id=token_doc["user_id"],
                family_id=token_doc["family_id"],
            )

    async def create_user(
        self,
        *,
        tenant_id: str,
        username: str,
        password: str,
        roles: frozenset[Role],
        email: str | None,
        actor_id: str,
    ) -> dict:
        user = await self.repository.create_user(
            username=username.strip().lower(),
            hashed_password=hash_secret(password),
            roles=sorted(role.value for role in roles),
            tenant_id=tenant_id,
            email=email.strip().lower() if email else None,
        )
        await self.repository.record_audit_event(
            "auth.user_created",
            user_id=user["user_id"],
            actor_id=actor_id,
            tenant_id=tenant_id,
        )
        return user

    async def set_user_active(
        self, *, user_id: str, is_active: bool, actor: Principal
    ) -> dict:
        user = await self.repository.set_user_active(user_id, is_active)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await self.repository.record_audit_event(
            "auth.user_status_changed",
            user_id=user_id,
            actor_id=actor.user_id,
            tenant_id=actor.tenant_id,
            is_active=is_active,
        )
        return user
