from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict

from app.auth.dependencies import get_current_user
from app.auth.tokens import Principal
from app.copilot.dependencies import get_runtime_rag_service
from ai_layer.rag.service import RAGService

router = APIRouter(prefix="/api/v1/copilot/memory", tags=["Copilot Memory"])


class MemoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent: bool


async def get_memory_service(request: Request):
    return (await get_runtime_rag_service(request)).memory


def _scope(principal: Principal, domain_id: str):
    return RAGService.build_memory_scope(
        tenant_id=principal.tenant_id,
        domain_id=domain_id,
        user_id=principal.user_id,
        session_id="memory-management",
        conversation_revision=0,
    )


@router.get("")
async def get_memory(
    domain_id: Annotated[str, Query(min_length=1)] = "agriculture",
    principal: Principal = Depends(get_current_user),
    service: Any = Depends(get_memory_service),
):
    facts = await service.list_facts(_scope(principal, domain_id))
    return {"facts": [fact.model_dump(mode="json") for fact in facts]}

@router.patch("/{fact_id}")
async def patch_memory(
    fact_id: str,
    updates: MemoryUpdate,
    domain_id: Annotated[str, Query(min_length=1)] = "agriculture",
    principal: Principal = Depends(get_current_user),
    service: Any = Depends(get_memory_service),
):
    try:
        fact = await service.confirm_fact(
            _scope(principal, domain_id), fact_id, consent=updates.consent
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": fact.status.value, "fact": fact.model_dump(mode="json")}

@router.delete("/{fact_id}")
async def delete_memory(
    fact_id: str,
    domain_id: Annotated[str, Query(min_length=1)] = "agriculture",
    principal: Principal = Depends(get_current_user),
    service: Any = Depends(get_memory_service),
):
    try:
        fact = await service.forget_fact(_scope(principal, domain_id), fact_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": fact.status.value, "fact": fact.model_dump(mode="json")}
