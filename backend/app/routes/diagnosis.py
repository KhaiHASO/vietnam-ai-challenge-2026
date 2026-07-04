from fastapi import APIRouter, Body, Depends, File, UploadFile

from app.schemas.diagnosis import (
    AnalyzeImageRequest,
    DiagnosisCaseCreate,
    FinalizeDiagnosisRequest,
    SymptomAnswersRequest,
)
from app.services.diagnosis_service import DiagnosisService

router = APIRouter(prefix="/api/diagnosis", tags=["Diagnosis"])


def get_diagnosis_service() -> DiagnosisService:
    return DiagnosisService()


@router.post("/cases", status_code=201)
async def create_case(
    request: DiagnosisCaseCreate,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.create_case(request)


@router.post("/cases/{case_id}/images", status_code=201)
async def upload_case_image(
    case_id: str,
    image: UploadFile = File(...),
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.upload_image(case_id, image)


@router.post("/cases/{case_id}/analyze-image")
async def analyze_case_image(
    case_id: str,
    request: AnalyzeImageRequest | None = Body(default=None),
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.analyze_image(case_id, request or AnalyzeImageRequest())


@router.get("/cases/{case_id}/symptom-questions")
async def get_symptom_questions(
    case_id: str,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.get_symptom_questions(case_id)


@router.post("/cases/{case_id}/symptom-answers", status_code=201)
async def save_symptom_answers(
    case_id: str,
    request: SymptomAnswersRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.save_symptom_answers(case_id, request)


@router.post("/cases/{case_id}/finalize")
async def finalize_case(
    case_id: str,
    request: FinalizeDiagnosisRequest | None = Body(default=None),
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> dict[str, object]:
    return await service.finalize_case(case_id, request or FinalizeDiagnosisRequest())
