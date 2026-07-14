import pytest
import jwt

from app.auth.contracts import Principal, Role
from app.auth.tokens import ALGORITHM
from app.core.config import settings

def test_access_token_round_trip(token_service) -> None:
    principal = Principal(
        user_id="test-user-id",
        tenant_id="tenant-a",
        roles=frozenset({Role.OPERATOR}),
    )
    encoded = token_service.create_access_token(principal)
    decoded = token_service.decode_access_token(encoded)
    assert decoded.user_id == principal.user_id
    assert decoded.tenant_id == "tenant-a"
    assert decoded.roles == frozenset({Role.OPERATOR})

    payload = jwt.decode(
        encoded,
        settings.jwt_secret.get_secret_value(),
        algorithms=[ALGORITHM],
    )
    assert payload["tenant_id"] == "tenant-a"
    assert payload["jti"]

def test_expired_token_raises_error(token_service) -> None:
    principal = Principal(user_id="test", roles=frozenset())
    # Create an expired token by passing negative expiry
    encoded = token_service.create_access_token(principal, expires_delta_minutes=-1)
    with pytest.raises(Exception) as exc:
        token_service.decode_access_token(encoded)
    assert "expired" in str(exc.value).lower()
