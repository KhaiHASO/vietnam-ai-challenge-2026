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

    # Return domain configuration for this request without mutating global state.

    return {
        "success": True,
        "active_domain": "agriculture",
        "db_path": ai_settings.db_path_for(normalized_domain).as_posix(),
        "vector_db_path": ai_settings.vector_db_path_for(normalized_domain).as_posix(),
        "message": "Hệ thống đã khóa cố định ở miền Nông nghiệp (AGRICULTURE).",
    }


def get_domain_status() -> dict[str, object]:
    return {
        "active_domain": "agriculture",
        "model_name": ai_settings.MODEL_NAME,
        "db_path": ai_settings.db_path_for("agriculture").as_posix(),
        "vector_db_path": ai_settings.vector_db_path_for("agriculture").as_posix(),
    }
