from app.db.schema import REQUIRED_COLLECTION_NAMES


def test_approval_state_has_a_validated_collection() -> None:
    assert "approvals" in REQUIRED_COLLECTION_NAMES
