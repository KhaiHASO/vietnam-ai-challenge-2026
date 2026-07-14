from collections.abc import Iterable

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.contracts import Principal, Role
from app.auth.repository import AuthRepository
from app.auth.service import AuthService
from app.auth.tokens import TokenService
from app.core.config import settings

security = HTTPBearer()


def get_token_service() -> TokenService:
    return TokenService()


def get_auth_repository() -> AuthRepository:
    return AuthRepository()


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(repository, token_service)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: TokenService = Depends(get_token_service),
) -> Principal:
    try:
        return token_service.decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_roles(required_roles: Iterable[Role]):
    required = frozenset(required_roles)

    def role_checker(principal: Principal = Depends(get_current_user)) -> Principal:
        if principal.roles.isdisjoint(required):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return role_checker


def require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if not origin or settings.cors_origin_list == ["*"]:
        return
    if origin.rstrip("/") not in {
        allowed.rstrip("/") for allowed in settings.cors_origin_list
    }:
        raise HTTPException(status_code=403, detail="Cross-origin auth request denied")
