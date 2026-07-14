from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.auth.contracts import (
    CreateUserRequest,
    LoginRequest,
    Principal,
    Role,
    SessionToken,
    UserStatusRequest,
    UserView,
)
from app.auth.dependencies import (
    get_auth_service,
    get_current_user,
    require_roles,
    require_same_origin,
)
from app.auth.service import AuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
admin_router = APIRouter(prefix="/admin", tags=["Administration"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="strict",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )


@router.post("/login", response_model=SessionToken)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionToken:
    session = await auth_service.login(request.username, request.password)
    _set_refresh_cookie(response, session.refresh_token)
    return session


@router.post("/refresh", response_model=SessionToken)
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    _: None = Depends(require_same_origin),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionToken:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    session = await auth_service.rotate_refresh(refresh_token)
    _set_refresh_cookie(response, session.refresh_token)
    return session


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    _: None = Depends(require_same_origin),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    if refresh_token:
        await auth_service.logout(refresh_token)
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return {"status": "logged_out"}


@router.get("/me", response_model=Principal)
async def get_me(principal: Principal = Depends(get_current_user)) -> Principal:
    return principal


@admin_router.post(
    "/users", response_model=UserView, status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: CreateUserRequest,
    principal: Principal = Depends(require_roles([Role.ADMIN])),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    return await auth_service.create_user(
        tenant_id=principal.tenant_id,
        username=request.username,
        password=request.password,
        roles=request.roles,
        email=request.email,
        actor_id=principal.user_id,
    )


@admin_router.patch("/users/{user_id}/status", response_model=UserView)
async def set_user_status(
    user_id: str,
    request: UserStatusRequest,
    principal: Principal = Depends(require_roles([Role.ADMIN])),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    return await auth_service.set_user_active(
        user_id=user_id, is_active=request.is_active, actor=principal
    )
