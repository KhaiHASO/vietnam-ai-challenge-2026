from fastapi import APIRouter, Depends
from typing import Any

from app.auth.dependencies import get_current_user
from app.auth.tokens import Principal

router = APIRouter(prefix="/api/v1/copilot/memory", tags=["Copilot Memory"])

@router.get("")
async def get_memory(principal: Principal = Depends(get_current_user)):
    return {"facts": []}

@router.patch("/{fact_id}")
async def patch_memory(
    fact_id: str,
    updates: dict[str, Any],
    principal: Principal = Depends(get_current_user),
):
    return {"status": "ok"}

@router.delete("/{fact_id}")
async def delete_memory(
    fact_id: str,
    principal: Principal = Depends(get_current_user),
):
    return {"status": "ok"}
