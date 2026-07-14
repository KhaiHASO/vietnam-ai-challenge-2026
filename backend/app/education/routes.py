from __future__ import annotations

import hashlib
import json
from functools import lru_cache

from fastapi import HTTPException, status
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from app.auth.contracts import Principal, Role
from app.auth.dependencies import get_current_user
from ai_layer.rag.registries.curriculum_graph import load_curriculum_graph

from .authorization import (
    can_read_class,
    can_read_student,
    class_by_id,
    get_seed_directory,
    not_found,
    require_education_role,
    require_seed_tenant,
    student_by_id,
)
from .contracts import AttemptEvent
from .knowledge_tracing import KnowledgeTracingRuntime
from .repository import (
    AttemptIdempotencyConflict,
    InMemoryAttemptRepository,
    InMemoryLearnerStateRepository,
)
from .state_update_service import LearnerStateUpdateService


router = APIRouter(prefix="/api/v1/education", tags=["Education"])

GRAPH_VERSION = "gdpt2018-v1"
QUESTION_VERSION = "questions-v1"
POLICY_VERSION = "mathpath-policy-v1"
MODEL_VERSION = "bkt-elo-v1"
GRAPH_PATH = "domains/education-mathpath/knowledge/curriculum_graph.yaml"


class StudentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: str
    pseudonym: str
    grade: int
    class_id: str


class ClassRoster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_id: str
    label: str
    grade: int
    teacher_id: str
    students: list[StudentSummary]


class PracticeSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(min_length=1)
    target_skill_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1, max_length=256)


class VersionPins(BaseModel):
    model_config = ConfigDict(extra="forbid")

    graph: str
    question: str
    policy: str
    model: str


class PracticeSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    student_id: str
    target_skill_id: str
    created: bool
    versions: VersionPins


class StepAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: str = Field(min_length=1, max_length=256)
    question_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    step_index: int = Field(ge=0)
    raw_step: str = Field(min_length=1, max_length=4000)
    normalized_step: str | None = Field(default=None, max_length=4000)
    verification_status: str
    math_evidence_hash: str
    math_tool_version: str = Field(min_length=1)
    question_difficulty: float = Field(ge=0, le=1)
    hint_level: int = Field(default=0, ge=0, le=3)
    misconception_id: str | None = None


class LearnerStateUpdateView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    reason_code: str
    resulting_revision: int | None


class StepAttemptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt_id: str
    session_id: str
    student_id: str
    versions: VersionPins
    state_update: LearnerStateUpdateView
    state: dict[str, object] | None


class _PracticeSessionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str
    tenant_id: str
    student_id: str
    target_skill_id: str
    idempotency_key: str
    request_hash: str
    versions: VersionPins


class _PracticeSessionStore:
    def __init__(self) -> None:
        self._by_key: dict[tuple[str, str], _PracticeSessionRecord] = {}
        self._by_id: dict[tuple[str, str], _PracticeSessionRecord] = {}

    def create_or_get(
        self,
        *,
        tenant_id: str,
        request: PracticeSessionRequest,
    ) -> tuple[_PracticeSessionRecord, bool]:
        request_hash = _request_hash(request.model_dump(mode="json"))
        key = (tenant_id, request.idempotency_key)
        existing = self._by_key.get(key)
        if existing is not None:
            if existing.request_hash != request_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key already used with a different payload",
                )
            return existing, False
        session_id = "PS-" + hashlib.sha256(
            f"{tenant_id}:{request.idempotency_key}".encode("utf-8")
        ).hexdigest()[:16].upper()
        record = _PracticeSessionRecord(
            session_id=session_id,
            tenant_id=tenant_id,
            student_id=request.student_id,
            target_skill_id=request.target_skill_id,
            idempotency_key=request.idempotency_key,
            request_hash=request_hash,
            versions=_versions(),
        )
        self._by_key[key] = record
        self._by_id[(tenant_id, session_id)] = record
        return record, True

    def get(self, tenant_id: str, session_id: str) -> _PracticeSessionRecord:
        record = self._by_id.get((tenant_id, session_id))
        if record is None:
            raise not_found()
        return record


def _request_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _versions() -> VersionPins:
    return VersionPins(
        graph=GRAPH_VERSION,
        question=QUESTION_VERSION,
        policy=POLICY_VERSION,
        model=MODEL_VERSION,
    )


@lru_cache(maxsize=1)
def get_practice_session_store() -> _PracticeSessionStore:
    return _PracticeSessionStore()


@lru_cache(maxsize=1)
def get_attempt_repository() -> InMemoryAttemptRepository:
    return InMemoryAttemptRepository()


@lru_cache(maxsize=1)
def get_learner_state_repository() -> InMemoryLearnerStateRepository:
    return InMemoryLearnerStateRepository()


@lru_cache(maxsize=1)
def get_state_update_service() -> LearnerStateUpdateService:
    runtime = KnowledgeTracingRuntime(graph=load_curriculum_graph(GRAPH_PATH))
    return LearnerStateUpdateService(
        runtime=runtime,
        repository=get_learner_state_repository(),
    )


def _question_skill(question_id: str) -> str:
    seed = get_seed_directory()
    for question in seed.questions:
        if question.question_id == question_id:
            return question.skill_id
    raise not_found()


@router.get("/classes/{class_id}", response_model=ClassRoster)
async def get_class_roster(
    class_id: str,
    principal: Principal = Depends(get_current_user),
) -> ClassRoster:
    require_education_role(principal, {Role.ADMIN, Role.TEACHER})
    seed = get_seed_directory()
    require_seed_tenant(principal, seed)
    classroom = class_by_id(seed, class_id)
    if not can_read_class(principal, classroom):
        raise not_found()
    students = [
        StudentSummary(
            student_id=student.student_id,
            pseudonym=student.pseudonym,
            grade=student.grade,
            class_id=student.class_id,
        )
        for student in seed.students
        if student.class_id == classroom.class_id
    ]
    return ClassRoster(
        class_id=classroom.class_id,
        label=classroom.label,
        grade=classroom.grade,
        teacher_id=classroom.teacher_id,
        students=students,
    )


@router.get("/students/{student_id}/summary", response_model=StudentSummary)
async def get_student_summary(
    student_id: str,
    principal: Principal = Depends(get_current_user),
) -> StudentSummary:
    require_education_role(principal, {Role.ADMIN, Role.TEACHER, Role.STUDENT})
    seed = get_seed_directory()
    require_seed_tenant(principal, seed)
    student = student_by_id(seed, student_id)
    classroom = class_by_id(seed, student.class_id)
    if not can_read_student(principal, student=student, classroom=classroom):
        raise not_found()
    return StudentSummary(
        student_id=student.student_id,
        pseudonym=student.pseudonym,
        grade=student.grade,
        class_id=student.class_id,
    )


@router.post("/practice-sessions", response_model=PracticeSessionResponse)
async def create_practice_session(
    request: PracticeSessionRequest,
    principal: Principal = Depends(get_current_user),
) -> PracticeSessionResponse:
    require_education_role(principal, {Role.ADMIN, Role.TEACHER, Role.STUDENT})
    seed = get_seed_directory()
    require_seed_tenant(principal, seed)
    student = student_by_id(seed, request.student_id)
    classroom = class_by_id(seed, student.class_id)
    if not can_read_student(principal, student=student, classroom=classroom):
        raise not_found()
    record, created = get_practice_session_store().create_or_get(
        tenant_id=principal.tenant_id,
        request=request,
    )
    return PracticeSessionResponse(
        session_id=record.session_id,
        student_id=record.student_id,
        target_skill_id=record.target_skill_id,
        created=created,
        versions=record.versions,
    )


@router.post(
    "/practice-sessions/{session_id}/step-attempts",
    response_model=StepAttemptResponse,
)
async def create_step_attempt(
    session_id: str,
    request: StepAttemptRequest,
    principal: Principal = Depends(get_current_user),
) -> StepAttemptResponse:
    require_education_role(principal, {Role.ADMIN, Role.TEACHER, Role.STUDENT})
    seed = get_seed_directory()
    require_seed_tenant(principal, seed)
    session = get_practice_session_store().get(principal.tenant_id, session_id)
    student = student_by_id(seed, session.student_id)
    classroom = class_by_id(seed, student.class_id)
    if not can_read_student(principal, student=student, classroom=classroom):
        raise not_found()
    if request.skill_id != session.target_skill_id:
        raise HTTPException(status_code=422, detail="Attempt skill must match session target")
    if _question_skill(request.question_id) != request.skill_id:
        raise HTTPException(status_code=422, detail="Question skill mismatch")

    attempt_id = "ATT-API-" + hashlib.sha256(
        f"{principal.tenant_id}:{session_id}:{request.idempotency_key}".encode("utf-8")
    ).hexdigest()[:16].upper()
    attempt = AttemptEvent(
        attempt_id=attempt_id,
        tenant_id=principal.tenant_id,
        student_id=session.student_id,
        session_id=session.session_id,
        question_id=request.question_id,
        skill_id=request.skill_id,
        step_index=request.step_index,
        raw_step=request.raw_step,
        normalized_step=request.normalized_step,
        verification_status=request.verification_status,
        evidence={
            "validation_status": "accepted",
            "math_tool": {
                "status": request.verification_status,
                "tool_version": request.math_tool_version,
                "evidence_hash": request.math_evidence_hash,
                "trace_id": f"{attempt_id}:math",
            },
            "question": {
                "skill_id": request.skill_id,
                "version": QUESTION_VERSION,
                "difficulty": request.question_difficulty,
            },
            "hint_level": request.hint_level,
            "misconception_id": request.misconception_id,
        },
        graph_version=GRAPH_VERSION,
        question_version=QUESTION_VERSION,
        policy_version=POLICY_VERSION,
        model_version=MODEL_VERSION,
        idempotency_key=request.idempotency_key,
    )
    try:
        stored_attempt = await get_attempt_repository().append(attempt)
    except AttemptIdempotencyConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    update = await get_state_update_service().process_attempt(stored_attempt)
    return StepAttemptResponse(
        attempt_id=stored_attempt.attempt_id,
        session_id=session.session_id,
        student_id=session.student_id,
        versions=session.versions,
        state_update=LearnerStateUpdateView(
            status=update.status,
            reason_code=update.reason_code,
            resulting_revision=(
                update.state.revision if update.state is not None else None
            ),
        ),
        state=update.state.model_dump(mode="json") if update.state is not None else None,
    )
