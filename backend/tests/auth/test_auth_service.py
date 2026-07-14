import pytest
import asyncio

from app.auth.contracts import SessionToken

@pytest.mark.asyncio
async def test_refresh_reuse_revokes_the_token_family(auth_service, auth_repository) -> None:
    # 1. Issue initial session
    first_session = await auth_service.issue_session(
        user_id="user1", tenant_id="single", roles=["operator"]
    )
    
    # 2. Rotate with the valid refresh token -> yields second session
    second_session = await auth_service.rotate_refresh(first_session.refresh_token)
    
    # 3. Attempt to use the FIRST refresh token again (which was already rotated)
    # This simulates an attacker or stale client reusing an old refresh token
    with pytest.raises(Exception) as exc:
        await auth_service.rotate_refresh(first_session.refresh_token)
    
    assert "revoked" in str(exc.value).lower() or "reuse" in str(exc.value).lower()
    
    # 4. Verify that the ENTIRE token family is now revoked in the repository
    assert await auth_repository.is_family_revoked(first_session.family_id)


@pytest.mark.asyncio
async def test_concurrent_refresh_rotation_allows_at_most_one_success(
    auth_service, auth_repository
) -> None:
    first = await auth_service.issue_session(
        user_id="user1", tenant_id="single", roles=["operator"]
    )

    results = await asyncio.gather(
        auth_service.rotate_refresh(first.refresh_token),
        auth_service.rotate_refresh(first.refresh_token),
        return_exceptions=True,
    )

    successes = [result for result in results if isinstance(result, SessionToken)]
    failures = [result for result in results if isinstance(result, Exception)]
    assert len(successes) <= 1
    assert failures
    assert await auth_repository.is_family_revoked(first.family_id)
    assert any(event["event_type"] == "auth.refresh_reuse" for event in auth_repository.audit_events)
