from fastapi import HTTPException

from ai_layer.approval.hitl import hitl_manager


def get_pending_approvals() -> list[dict[str, object]]:
    return hitl_manager.get_pending_approvals()


def approve_action(approval_id: str) -> dict[str, object]:
    result = hitl_manager.approve_action(approval_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


def reject_action(approval_id: str) -> dict[str, object]:
    result = hitl_manager.reject_action(approval_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
