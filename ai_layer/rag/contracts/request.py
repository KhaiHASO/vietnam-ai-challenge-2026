from pydantic import BaseModel, Field, field_validator, ConfigDict
import uuid

class CopilotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    user_id: str
    tenant_id: str
    domain_id: str
    query: str
    expected_conversation_revision: int = 0
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be blank")
        return v
