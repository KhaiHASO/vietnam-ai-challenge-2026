import pytest

from app.auth.bootstrap import bootstrap_first_admin


class Repository:
    def __init__(self) -> None:
        self.users: list[dict] = []
        self.events: list[str] = []

    async def count_users(self) -> int:
        return len(self.users)

    async def create_user(self, **kwargs):
        record = {"user_id": "admin-1", **kwargs}
        self.users.append(record)
        return record

    async def record_audit_event(self, event_type: str, **kwargs) -> None:
        self.events.append(event_type)


@pytest.mark.asyncio
async def test_bootstrap_creates_only_the_first_admin() -> None:
    repository = Repository()
    created = await bootstrap_first_admin(repository, username="root", password="long-enough-secret")
    assert created is not None
    assert created["roles"] == ["admin"]
    assert await bootstrap_first_admin(repository, username="root", password="long-enough-secret") is None
    assert repository.events == ["auth.bootstrap_admin_created"]
