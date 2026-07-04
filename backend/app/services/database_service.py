from ai_layer.tools.db_mock import DEFAULT_AGRICULTURE_STATE, load_db, save_db


def get_database_state() -> dict[str, object]:
    return load_db()


def reset_database_state() -> dict[str, object]:
    save_db(DEFAULT_AGRICULTURE_STATE)
    return {
        "success": True,
        "message": "Cơ sở dữ liệu Nông nghiệp (AGRICULTURE) đã được đặt lại mặc định.",
    }
