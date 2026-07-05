import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.schemas.diagnosis import (
    AnalyzeImageRequest,
    DiagnosisCaseCreate,
    FinalizeDiagnosisRequest,
    SymptomAnswersRequest,
)
from app.services.agent_log_service import AgentLogService
from app.services.pytorch_report_service import PyTorchReportService
from app.services.reasoning_service import ReasoningService
from app.services.safety_ipm_service import SafetyIpmService
from app.services.vision_service import VisionService

logger = logging.getLogger("backend.diagnosis")

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _case_not_found(case_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Diagnosis case '{case_id}' not found")


def _upload_error(
    status_code: int,
    code: str,
    message: str,
    **details: Any,
) -> HTTPException:
    payload = {"code": code, "message": message}
    payload.update({key: value for key, value in details.items() if value is not None})
    return HTTPException(status_code=status_code, detail=payload)


def _join_answers(answers: list[dict[str, Any]], questions: list[dict[str, Any]]) -> str:
    question_by_id = {item["question_id"]: item["text"] for item in questions}
    lines = []
    for answer in answers:
        question = question_by_id.get(answer["question_id"], answer["question_id"])
        lines.append(f"- {question}: {answer.get('answer')}")
    return "\n".join(lines)


class DiagnosisService:
    def __init__(
        self,
        repository: DiagnosisRepository | None = None,
        vision_service: VisionService | None = None,
        reasoning_service: ReasoningService | None = None,
        safety_ipm_service: SafetyIpmService | None = None,
        pytorch_report_service: PyTorchReportService | None = None,
    ) -> None:
        self.repository = repository or DiagnosisRepository()
        self.vision_service = vision_service or VisionService()
        self.reasoning_service = reasoning_service or ReasoningService()
        self.safety_ipm_service = safety_ipm_service or SafetyIpmService()
        self.pytorch_report_service = pytorch_report_service or PyTorchReportService()
        self.agent_log_service = AgentLogService(self.repository)

    async def create_case(self, request: DiagnosisCaseCreate) -> dict[str, Any]:
        now = _now()
        case_id = _new_id("case")
        status = "created"

        if request.image_url:
            image_id = _new_id("img")
            img_filename = request.image_url.replace("\\", "/").split("/")[-1]
            img_doc = {
                "image_id": image_id,
                "case_id": case_id,
                "uri": request.image_url,
                "filename": img_filename,
                "original_filename": img_filename,
                "content_type": "image/jpeg",
                "size_bytes": 0,
                "status": "uploaded",
                "created_at": now,
                "updated_at": now,
            }
            await self.repository.insert_one("case_images", img_doc)
            status = "image_uploaded"

        document = {
            "case_id": case_id,
            "farm_id": request.farm_id,
            "crop": request.crop.strip().lower(),
            "status": status,
            "summary": request.summary,
            "location": request.location,
            "notes": request.notes,
            "image_url": request.image_url,
            "risk_level": None,
            "needs_expert_review": False,
            "created_at": now,
            "updated_at": now,
        }
        return await self.repository.insert_one("diagnosis_cases", document)

    async def upload_image(self, case_id: str, image: UploadFile) -> dict[str, Any]:
        case = await self.repository.find_one("diagnosis_cases", {"case_id": case_id})
        if not case:
            raise _case_not_found(case_id)

        if not image.filename:
            raise _upload_error(
                400,
                "UPLOAD_MISSING_FILENAME",
                "Uploaded image must have a filename.",
            )

        extension = image.filename.rsplit(".", 1)[-1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise _upload_error(
                400,
                "UPLOAD_INVALID_EXTENSION",
                "Unsupported image extension.",
                extension=extension,
                allowed_extensions=sorted(ALLOWED_IMAGE_EXTENSIONS),
            )

        image_id = _new_id("img")
        case_dir = settings.upload_root_path / "diagnosis_cases" / case_id
        file_path = case_dir / f"{image_id}.{extension}"

        try:
            content = await image.read()
        except Exception as exc:
            logger.warning("Could not read uploaded image: %s", exc.__class__.__name__)
            raise _upload_error(
                400,
                "UPLOAD_READ_ERROR",
                "Could not read uploaded image.",
            ) from exc

        if not content:
            raise _upload_error(
                400,
                "UPLOAD_EMPTY_FILE",
                "Uploaded image is empty.",
            )

        try:
            case_dir.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
        except OSError as exc:
            logger.warning("Could not store uploaded image: %s", exc.__class__.__name__)
            raise _upload_error(
                500,
                "UPLOAD_STORAGE_ERROR",
                "Could not store uploaded image.",
            ) from exc

        now = _now()
        original_filename = image.filename.replace("\\", "/").split("/")[-1]

        document = {
            "image_id": image_id,
            "case_id": case_id,
            "uri": str(file_path),
            "filename": file_path.name,
            "original_filename": original_filename,
            "content_type": image.content_type or "application/octet-stream",
            "size_bytes": len(content),
            "status": "uploaded",
            "created_at": now,
            "updated_at": now,
        }

        await self.repository.insert_one("case_images", document)
        await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {"status": "image_uploaded", "updated_at": now},
        )
        return document

    async def analyze_image(self, case_id: str, request: AnalyzeImageRequest) -> dict[str, Any]:
        case = await self.repository.find_one("diagnosis_cases", {"case_id": case_id})
        if not case:
            raise _case_not_found(case_id)

        image_query = {"case_id": case_id}
        if request.image_id:
            image_query["image_id"] = request.image_id

        image = await self.repository.find_one(
            "case_images",
            image_query,
            sort=[("created_at", -1)],
        )
        if not image:
            raise HTTPException(status_code=400, detail="No uploaded image found for this case")

        image_path = image["uri"]
        crop_hint = request.crop_hint or case.get("crop") or ""
        started_at = time.perf_counter()

        try:
            vision_report = self.vision_service.analyze_image(
                image_path=image_path,
                crop_hint=crop_hint,
                original_filename=image.get("original_filename", ""),
            )
        except RuntimeError:
            logger.warning("Vision analysis failed for case %s", case_id)
            raise HTTPException(status_code=500, detail="Vision analysis failed")

        vision_result = vision_report["raw"]
        triage_result = self.pytorch_report_service.assess_risk(
            vision_result=vision_result,
            metadata=request.metadata,
        )

        now = _now()
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        result_id = _new_id("vision")
        agent_log = await self.agent_log_service.record(
            case_id=case_id,
            agent="VisionPyTorchAnalysisAgent",
            status="done",
            trace={
                "result_id": result_id,
                "image_id": image["image_id"],
                "vision_engine": vision_result.get("primary_engine"),
                "triage_engine": triage_result.get("engine"),
                "vision_fallback_used": bool(vision_result.get("fallback_used")),
                "triage_fallback_used": bool(triage_result.get("fallback_used")),
            },
            duration_ms=duration_ms,
        )
        ai_response = self.safety_ipm_service.build_ai_response(
            vision_report=vision_report,
            triage_result=triage_result,
            agent_logs=[agent_log],
        )
        result_document = {
            "result_id": result_id,
            "case_id": case_id,
            "image_id": image["image_id"],
            "crop_hint": crop_hint,
            "vision": vision_result,
            "image_quality": vision_report["image_quality"],
            "pytorch_triage": triage_result,
            "ai_response": ai_response,
            "created_at": now,
            "updated_at": now,
        }
        await self.repository.insert_one("vision_results", result_document)

        await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {
                "status": "image_analyzed",
                "risk_level": triage_result.get("risk_level"),
                "summary": vision_result.get("final_disease_vi"),
                "needs_expert_review": ai_response["expert_required"],
                "updated_at": now,
            },
        )
        return {**result_document, **ai_response}

    async def get_symptom_questions(self, case_id: str) -> dict[str, Any]:
        case = await self.repository.find_one("diagnosis_cases", {"case_id": case_id})
        if not case:
            raise _case_not_found(case_id)

        existing = await self.repository.find_many(
            "symptom_questions",
            {"case_id": case_id},
            sort=[("order", 1)],
        )
        if existing:
            return {"case_id": case_id, "questions": existing}

        vision_document = await self.repository.find_one(
            "vision_results",
            {"case_id": case_id},
            sort=[("created_at", -1)],
        )
        if not vision_document:
            raise HTTPException(status_code=400, detail="Analyze an image before requesting symptom questions")

        now = _now()
        question_docs = []
        questions = vision_document.get("ai_response", {}).get("follow_up_questions")
        if not questions:
            questions = self.safety_ipm_service.build_follow_up_questions(
                vision_document.get("vision", {})
            )

        for order, text in enumerate(questions, start=1):
            question_docs.append(
                {
                    "question_id": _new_id("question"),
                    "case_id": case_id,
                    "text": text,
                    "type": "text",
                    "options": [],
                    "order": order,
                    "source": "diagnosis_workflow",
                    "created_at": now,
                    "updated_at": now,
                }
            )

        await self.repository.insert_many("symptom_questions", question_docs)
        await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {"status": "symptom_questions_ready", "updated_at": now},
        )
        return {"case_id": case_id, "questions": question_docs}

    async def save_symptom_answers(
        self,
        case_id: str,
        request: SymptomAnswersRequest,
    ) -> dict[str, Any]:
        case = await self.repository.find_one("diagnosis_cases", {"case_id": case_id})
        if not case:
            raise _case_not_found(case_id)

        questions = await self.repository.find_many("symptom_questions", {"case_id": case_id})
        if not questions:
            raise HTTPException(status_code=400, detail="Request symptom questions before saving answers")

        valid_question_ids = {question["question_id"] for question in questions}
        invalid = [
            answer.question_id
            for answer in request.answers
            if answer.question_id not in valid_question_ids
        ]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Unknown question_id: {invalid[0]}")

        now = _now()
        answer_docs = [
            {
                "answer_id": _new_id("answer"),
                "case_id": case_id,
                "question_id": answer.question_id,
                "answer": answer.answer,
                "created_at": now,
                "updated_at": now,
            }
            for answer in request.answers
        ]
        await self.repository.insert_many("symptom_answers", answer_docs)
        await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {"status": "symptom_answers_saved", "updated_at": now},
        )
        return {"case_id": case_id, "answers": answer_docs}

    async def finalize_case(
        self,
        case_id: str,
        request: FinalizeDiagnosisRequest,
    ) -> dict[str, Any]:
        case = await self.repository.find_one("diagnosis_cases", {"case_id": case_id})
        if not case:
            raise _case_not_found(case_id)

        vision_document = await self.repository.find_one(
            "vision_results",
            {"case_id": case_id},
            sort=[("created_at", -1)],
        )
        if not vision_document:
            raise HTTPException(status_code=400, detail="Analyze an image before finalizing diagnosis")

        questions = await self.repository.find_many(
            "symptom_questions",
            {"case_id": case_id},
            sort=[("order", 1)],
        )
        answers = await self.repository.find_many(
            "symptom_answers",
            {"case_id": case_id},
            sort=[("created_at", 1)],
        )
        if not answers:
            raise HTTPException(status_code=400, detail="Save symptom answers before finalizing diagnosis")

        symptoms_text = _join_answers(answers, questions)
        if request.additional_notes:
            symptoms_text = f"{symptoms_text}\n- Ghi chú bổ sung: {request.additional_notes}"

        started_at = time.perf_counter()
        try:
            reasoning_result = self.reasoning_service.finalize_diagnosis(
                vision_result=vision_document["vision"],
                symptoms=symptoms_text,
                crop_hint=request.crop_hint or case.get("crop", ""),
            )
        except RuntimeError:
            logger.warning("Reasoning finalization failed for case %s", case_id)
            raise HTTPException(status_code=500, detail="Diagnosis finalization failed")

        now = _now()
        triage = vision_document.get("pytorch_triage", {})
        risk_level = triage.get("risk_level", "medium")
        treatment_plan = self.safety_ipm_service.build_treatment_plan(
            case_id=case_id,
            reasoning_result=reasoning_result,
            risk_level=risk_level,
        )
        await self.repository.insert_one("treatment_plans", treatment_plan)

        expert_review = self.safety_ipm_service.build_expert_review(
            case_id=case_id,
            risk_level=risk_level,
            treatment_plan=treatment_plan,
        )
        if expert_review:
            await self.repository.insert_one("expert_reviews", expert_review)
            await self.agent_log_service.record(
                case_id=case_id,
                agent="ExpertReviewCreationAgent",
                status="pending",
                trace={
                    "review_id": expert_review["review_id"],
                    "treatment_plan_id": treatment_plan["plan_id"],
                    "treatment_plan_status": treatment_plan["status"],
                    "risk_level": risk_level,
                    "reasons": expert_review.get("reasons", []),
                    "recommended_actions": expert_review.get("recommended_actions", []),
                },
                duration_ms=0.0,
            )

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        agent_log = await self.agent_log_service.record(
            case_id=case_id,
            agent="DiagnosisFinalizationAgent",
            status="done",
            trace={
                "reasoning_engine": reasoning_result.get("engine"),
                "reasoning_fallback_used": bool(reasoning_result.get("fallback_used")),
                "treatment_plan_id": treatment_plan["plan_id"],
                "treatment_plan_status": treatment_plan["status"],
                "expert_review_id": expert_review["review_id"] if expert_review else None,
                "expert_review_status": expert_review["status"] if expert_review else None,
                "expert_review_reasons": expert_review.get("reasons", []) if expert_review else [],
            },
            duration_ms=duration_ms,
        )

        previous_ai_response = vision_document.get("ai_response", {})
        vision_report = {
            "raw": vision_document["vision"],
            "image_quality": vision_document.get("image_quality")
            or previous_ai_response.get("image_quality", {}),
            "top_predictions": previous_ai_response.get("top_predictions")
            or vision_document["vision"].get("top_predictions", []),
        }
        ai_response = self.safety_ipm_service.build_ai_response(
            vision_report=vision_report,
            triage_result=triage,
            reasoning_result=reasoning_result,
            agent_logs=previous_ai_response.get("agent_logs", []) + [agent_log],
        )

        updated_case = await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {
                "status": "finalized",
                "risk_level": risk_level,
                "needs_expert_review": ai_response["expert_required"],
                "summary": treatment_plan["short_diagnosis"],
                "updated_at": now,
            },
        )

        result = {
            "case": updated_case,
            "vision_result": vision_document,
            "reasoning": reasoning_result,
            "treatment_plan": treatment_plan,
            "expert_review": expert_review,
            "ai_response": ai_response,
        }
        return {**result, **ai_response}
