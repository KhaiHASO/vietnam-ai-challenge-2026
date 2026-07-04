from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class SwitchDomainRequest(BaseModel):
    domain: str


class ApprovalActionRequest(BaseModel):
    pass
