import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from app.auth.contracts import Principal, Role
from app.core.config import settings

ALGORITHM = "HS256"


class TokenService:
    def create_access_token(
        self,
        principal: Principal,
        expires_delta_minutes: int | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        expire_minutes = (
            expires_delta_minutes
            if expires_delta_minutes is not None
            else settings.access_token_expire_minutes
        )
        payload: dict[str, Any] = {
            "sub": principal.user_id,
            "tenant_id": principal.tenant_id,
            "roles": sorted(role.value for role in principal.roles),
            "jti": str(uuid4()),
            "exp": now + timedelta(minutes=expire_minutes),
            "iat": now,
            "type": "access",
        }
        return jwt.encode(
            payload,
            settings.jwt_secret.get_secret_value(),
            algorithm=ALGORITHM,
        )

    def decode_access_token(self, token: str) -> Principal:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret.get_secret_value(),
                algorithms=[ALGORITHM],
                options={
                    "require": ["exp", "iat", "jti", "sub", "tenant_id", "type"]
                },
            )
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            return Principal(
                user_id=str(payload["sub"]),
                tenant_id=str(payload["tenant_id"]),
                roles=frozenset(Role(role) for role in payload.get("roles", [])),
            )
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc
        except (jwt.PyJWTError, KeyError, ValueError) as exc:
            raise ValueError("Could not validate credentials") from exc

    def generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)
