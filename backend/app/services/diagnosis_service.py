import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, UploadFile

from ai_layer.cropdoctor.agents.deepseek_reasoning_agent import DeepSeekReasoningAgent
from ai_layer.cropdoctor.agents.vision_consensus_agent import VisionConsensusAgent
from ai_layer.pytorch_engine.inference import predict_triage

from app.core.config import settings
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.schemas.diagnosis import (
    AnalyzeImageRequest,
    DiagnosisCaseCreate,
    FinalizeDiagnosisRequest,
    SymptomAnswersRequest,
)

logger = logging.getLogger("backend.diagnosis")

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

vision_agent = VisionConsensusAgent()
reasoning_agent = DeepSeekReasoningAgent()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _case_not_found(case_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Diagnosis case '{case_id}' not found")


def _question_texts(vision_result: dict[str, Any]) -> list[str]:
    label = vision_result.get("final_disease_label", "").lower()
    decision_status = vision_result.get("decision_status", "")

    questions = [
        "Vết bệnh xuất hiện đầu tiên ở lá già sát mặt đất hay lá non phía trên?",
        "Trong 7 ngày gần đây vườn có mưa lớn, sương đêm hoặc tưới phun lên lá không?",
        "Tỷ lệ cây hoặc diện tích lá bị ảnh hưởng ước tính là bao nhiêu phần trăm?",
    ]

    if "late_blight" in label:
        questions.append("Mặt dưới lá có lớp tơ trắng mỏng khi trời ẩm không?")
    elif "early_blight" in label:
        questions.append("Vết đốm có dạng vòng tròn đồng tâm như hình bia bắn không?")
    elif "bacterial" in label:
        questions.append("Trên quả hoặc mặt dưới lá có nốt sần nhỏ như mụn cóc không?")
    elif "healthy" in label:
        questions.append("Cây có dấu hiệu héo rũ ban ngày dù đất vẫn đủ ẩm không?")
    else:
        questions.append("Triệu chứng có lan nhanh sang cây bên cạnh trong 48 giờ gần nhất không?")

    if decision_status == "low_confidence_need_better_image_or_expert":
        questions.append("Bạn có thể chụp thêm ảnh cận cảnh mặt trên và mặt dưới lá trong ánh sáng tự nhiên không?")

    return questions


def _join_answers(answers: list[dict[str, Any]], questions: list[dict[str, Any]]) -> str:
    question_by_id = {item["question_id"]: item["text"] for item in questions}
    lines = []
    for answer in answers:
        question = question_by_id.get(answer["question_id"], answer["question_id"])
        lines.append(f"- {question}: {answer.get('answer')}")
    return "\n".join(lines)


def _treatment_plan_from_reasoning(
    case_id: str,
    reasoning_result: dict[str, Any],
) -> dict[str, Any]:
    content = reasoning_result.get("content", {})
    recommendations = content.get("safe_recommendations", [])
    return {
        "plan_id": _new_id("plan"),
        "case_id": case_id,
        "status": "draft",
        "diagnosis_level": content.get("diagnosis_level", "uncertain"),
        "short_diagnosis": content.get("short_diagnosis", "Chưa đủ dữ liệu chẩn đoán"),
        "recommendations": recommendations,
        "safety_notes": content.get("why", []),
        "when_to_call_expert": content.get("when_to_call_expert", []),
        "disclaimer": content.get("disclaimer", ""),
        "created_at": _now(),
        "updated_at": _now(),
    }


class DiagnosisService:
    def __init__(self, repository: DiagnosisRepository | None = None) -> None:
        self.repository = repository or DiagnosisRepository()

    async def create_case(self, request: DiagnosisCaseCreate) -> dict[str, Any]:
        now = _now()
        document = {
            "case_id": _new_id("case"),
            "farm_id": request.farm_id,
            "crop": request.crop.strip().lower(),
            "status": "created",
            "summary": request.summary,
            "location": request.location,
            "notes": request.notes,
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
            raise HTTPException(status_code=400, detail="Uploaded image must have a filename")

        extension = image.filename.rsplit(".", 1)[-1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported image extension: .{extension}")

        image_id = _new_id("img")
        case_dir = settings.upload_root_path / "diagnosis_cases" / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        file_path = case_dir / f"{image_id}.{extension}"

        content = await image.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded image is empty")

        file_path.write_bytes(content)

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
            vision_result = vision_agent.predict(
                image_path=image_path,
                crop_hint=crop_hint,
                original_filename=image.get("original_filename", ""),
            )
        except Exception:
            logger.exception("Vision analysis failed for case %s", case_id)
            raise HTTPException(status_code=500, detail="Vision analysis failed")

        description = " ".join(
            str(part)
            for part in (
                vision_result.get("final_disease_vi"),
                vision_result.get("final_disease_label"),
                vision_result.get("decision_status"),
            )
            if part
        )
        metadata = dict(request.metadata)
        metadata.setdefault("leaf_damage_percent", 0.0)
        try:
            triage_result = predict_triage(description, metadata)
        except Exception:
            logger.exception("PyTorch triage failed for case %s", case_id)
            triage_result = {
                "risk_level": "medium",
                "priority": 0.5,
                "needs_human_review": True,
                "confidence": 0.0,
                "top_factors": ["pytorch_error_fallback"],
                "model_version": "fallback",
                "engine": "error_fallback",
            }

        now = _now()
        result_document = {
            "result_id": _new_id("vision"),
            "case_id": case_id,
            "image_id": image["image_id"],
            "crop_hint": crop_hint,
            "vision": vision_result,
            "pytorch_triage": triage_result,
            "created_at": now,
            "updated_at": now,
        }
        await self.repository.insert_one("vision_results", result_document)

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        await self.repository.insert_one(
            "agent_logs",
            {
                "log_id": _new_id("log"),
                "case_id": case_id,
                "agent": "VisionPyTorchAnalysisAgent",
                "status": "done",
                "trace": {
                    "image_id": image["image_id"],
                    "vision_engine": vision_result.get("primary_engine"),
                    "triage_engine": triage_result.get("engine"),
                },
                "duration_ms": duration_ms,
                "created_at": now,
                "updated_at": now,
            },
        )

        await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {
                "status": "image_analyzed",
                "risk_level": triage_result.get("risk_level"),
                "summary": vision_result.get("final_disease_vi"),
                "updated_at": now,
            },
        )
        return result_document

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
        for order, text in enumerate(_question_texts(vision_document.get("vision", {})), start=1):
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
            reasoning_result = reasoning_agent.reason(
                vision_result=vision_document["vision"],
                symptoms=symptoms_text,
                crop_hint=request.crop_hint or case.get("crop", ""),
            )
        except Exception:
            logger.exception("Reasoning finalization failed for case %s", case_id)
            raise HTTPException(status_code=500, detail="Diagnosis finalization failed")

        now = _now()
        treatment_plan = _treatment_plan_from_reasoning(case_id, reasoning_result)
        await self.repository.insert_one("treatment_plans", treatment_plan)

        triage = vision_document.get("pytorch_triage", {})
        risk_level = triage.get("risk_level", "medium")
        expert_review = None
        if risk_level == "high":
            expert_review = {
                "review_id": _new_id("review"),
                "case_id": case_id,
                "status": "pending",
                "reviewer_id": None,
                "notes": "Tự động tạo do ca chẩn đoán có rủi ro cao.",
                "risk_level": risk_level,
                "reason": "high_risk_diagnosis_case",
                "created_at": now,
                "updated_at": now,
            }
            await self.repository.insert_one("expert_reviews", expert_review)

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        await self.repository.insert_one(
            "agent_logs",
            {
                "log_id": _new_id("log"),
                "case_id": case_id,
                "agent": "DiagnosisFinalizationAgent",
                "status": "done",
                "trace": {
                    "reasoning_engine": reasoning_result.get("engine"),
                    "treatment_plan_id": treatment_plan["plan_id"],
                    "expert_review_id": expert_review["review_id"] if expert_review else None,
                },
                "duration_ms": duration_ms,
                "created_at": now,
                "updated_at": now,
            },
        )

        updated_case = await self.repository.update_one(
            "diagnosis_cases",
            {"case_id": case_id},
            {
                "status": "finalized",
                "risk_level": risk_level,
                "needs_expert_review": expert_review is not None,
                "summary": treatment_plan["short_diagnosis"],
                "updated_at": now,
            },
        )

        return {
            "case": updated_case,
            "vision_result": vision_document,
            "reasoning": reasoning_result,
            "treatment_plan": treatment_plan,
            "expert_review": expert_review,
        }
