from fastapi import HTTPException

from ai_layer.config import settings as ai_settings
from ai_layer.rag.knowledge_base import seed_knowledge_base
from ai_layer.tools.db_mock import load_db


def switch_domain(domain: str) -> dict[str, object]:
    normalized_domain = domain.lower().strip()
    if normalized_domain != "agriculture":
        raise HTTPException(
            status_code=400,
            detail="Hệ thống đã được cấu hình chuyên biệt và chỉ hỗ trợ miền Nông nghiệp (agriculture).",
        )

    ai_settings.ACTIVE_DOMAIN = "agriculture"
    seed_knowledge_base()
    load_db()

    return {
        "success": True,
        "active_domain": "agriculture",
        "db_path": ai_settings.db_path,
        "vector_db_path": ai_settings.vector_db_path,
        "message": "Hệ thống đã khóa cố định ở miền Nông nghiệp (AGRICULTURE).",
    }


def get_domain_status() -> dict[str, object]:
    return {
        "active_domain": "agriculture",
        "model_name": ai_settings.MODEL_NAME,
        "db_path": ai_settings.db_path,
        "vector_db_path": ai_settings.vector_db_path,
    }
