from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class ApprovalActionRequest(BaseModel):
    pass
