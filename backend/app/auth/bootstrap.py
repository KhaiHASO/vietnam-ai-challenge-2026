"""Explicit, idempotent first-admin bootstrap for a fresh deployment."""

from typing import Any

from app.core.security import hash_secret


async def bootstrap_first_admin(repository: Any, *, username: str | None, password: str | None, tenant_id: str = "single") -> dict[str, Any] | None:
    if not username or not password:
        return None
    if len(password) < 12:
        raise ValueError("Bootstrap admin password must be at least 12 characters")
    if await repository.count_users() != 0:
        return None
    user = await repository.create_user(
        username=username.strip().lower(),
        hashed_password=hash_secret(password),
        roles=["admin"],
        tenant_id=tenant_id,
        email=None,
    )
    await repository.record_audit_event("auth.bootstrap_admin_created", user_id=user["user_id"], tenant_id=tenant_id)
    return user
