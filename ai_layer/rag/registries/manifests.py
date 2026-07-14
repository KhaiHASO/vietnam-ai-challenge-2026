from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CapabilityManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    capabilities: tuple[str, ...]
    supported_domains: tuple[str, ...]
    config_schema: dict[str, Any]
    risk_class: str
    lifecycle: str = "singleton"
    required: bool = False
    output_schema: dict[str, Any] | None = None


class MemoryPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed_fact_fields: tuple[str, ...]


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    similarity_threshold: float = Field(ge=0, le=1)
    top_k: int = Field(gt=0, le=100)
    minimum_source_diversity: int = Field(default=1, gt=0)
    maximum_age_days: int | None = Field(default=None, gt=0)


class ToolRiskClass(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    requires_approval: bool


class DomainManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str
    locale: str
    prompt_bundle_version: str
    policy_bundle_version: str
    validator_bundle_version: str
    memory_policy: MemoryPolicy
    retrieval: RetrievalConfig
    provider_order: tuple[str, ...]
    max_reflect_count: int = Field(ge=0, le=10)
    tool_risk_classes: tuple[ToolRiskClass, ...]
