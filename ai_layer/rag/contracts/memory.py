from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk_id: str
    document_id: str
    source_uri: str
    tenant_id: str
    domain_id: str
    index_revision: str
    score: float = Field(ge=0, le=1)
    content: str = Field(min_length=1)
    checksum: str = Field(min_length=1)
    source_title: str | None = None
    page_or_section: str | None = None
    document_status: Literal["active", "archived", "superseded"] = "active"
    published_at: datetime | None = None
    expires_at: datetime | None = None
    contradiction: bool = False
    evidence_type: Literal["knowledge", "tool"] = "knowledge"


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk_id: str
    inline_reference: str
    quoted_text: str | None = None
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_span(self) -> "Citation":
        if (self.start_char is None) != (self.end_char is None):
            raise ValueError("Citation span requires both start_char and end_char")
        if (
            self.start_char is not None
            and self.end_char is not None
            and self.end_char <= self.start_char
        ):
            raise ValueError("Citation end_char must be greater than start_char")
        return self
