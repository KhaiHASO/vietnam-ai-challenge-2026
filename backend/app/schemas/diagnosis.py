from typing import Any

from pydantic import BaseModel, Field


class DiagnosisCaseCreate(BaseModel):
    farm_id: str | None = None
    crop: str = Field(default="tomato", min_length=1)
    summary: str | None = None
    location: str | None = None
    notes: str | None = None


class DiagnosisCaseResponse(BaseModel):
    case_id: str
    status: str
    crop: str
    farm_id: str | None = None
    summary: str | None = None
    risk_level: str | None = None
    needs_expert_review: bool = False


class AnalyzeImageRequest(BaseModel):
    image_id: str | None = None
    crop_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SymptomAnswerInput(BaseModel):
    question_id: str
    answer: str | dict[str, Any] | list[Any]


class SymptomAnswersRequest(BaseModel):
    answers: list[SymptomAnswerInput] = Field(default_factory=list, min_length=1)


class FinalizeDiagnosisRequest(BaseModel):
    crop_hint: str | None = None
    additional_notes: str | None = None


class AIResponse(BaseModel):
    image_quality: dict[str, Any]
    top_predictions: list[dict[str, Any]]
    diagnosis: dict[str, Any]
    recommended_actions: list[str]
    follow_up_questions: list[str]
    risk_level: str
    confidence: float
    expert_required: bool
    agent_logs: list[dict[str, Any]]
