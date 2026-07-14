import pytest
from app.approvals.repository import InMemoryApprovalRepository, ApprovalRecord

@pytest.fixture
def repository():
    return InMemoryApprovalRepository()

@pytest.fixture
def approval():
    return ApprovalRecord(
        approval_id="a1",
        policy="test",
        proposed_action={},
        evidence=[],
        requester="u1",
        required_roles=["admin"],
        status="pending"
    )
