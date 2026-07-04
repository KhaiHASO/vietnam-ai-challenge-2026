import json
import os
import copy
from typing import Dict, Any
from ai_layer.config import settings

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except Exception:
    MongoClient = None
    PyMongoError = Exception

DEFAULT_SME_STATE = {
    "wallet": {
        "balance": 1500000,
        "currency": "VND"
    },
    "services": {
        "payment": {"status": "degraded", "log": "Timeout error in MoMo callback API since 14:30 PM."},
        "booking": {"status": "operational", "log": "All systems operational."},
        "vector_search": {"status": "operational", "log": "Local CUDA GPU index query response time < 5ms."}
    },
    "bookings": [
        {
            "booking_id": "BKG-88321A",
            "sport": "Pickleball",
            "court": "Court 1 - Premium",
            "date": "2026-07-02",
            "time": "18:00 - 20:00",
            "amount": 220000,
            "status": "Paid"
        },
        {
            "booking_id": "BKG-99212B",
            "sport": "Badminton",
            "court": "Court A",
            "date": "2026-07-03",
            "time": "08:00 - 10:00",
            "amount": 120000,
            "status": "Paid"
        }
    ],
    "tickets": [
        {
            "ticket_id": "TCK-5541A",
            "title": "Momo Deducted but no Booking",
            "service": "payment",
            "description": "User was deducted 220,000 VND but did not get booking code.",
            "priority": "High",
            "status": "Open"
        }
    ]
}

DEFAULT_EDUCATION_STATE = {
    "services": {
        "student_portal": {"status": "operational", "log": "Operational."},
        "grades_db": {"status": "operational", "log": "Syncing grades database hourly."},
        "risk_engine": {"status": "operational", "log": "PyTorch models loaded for SME/Edu/Agri."}
    },
    "students": [
        {
            "student_id": "STU-1001",
            "name": "Nguyễn Văn A",
            "major": "Computer Science",
            "prior_gpa": 3.4,
            "attendance_rate": 0.95,
            "late_submissions_count": 0,
            "lms_activity_score": 92.5,
            "midterm_grade": 8.5
        },
        {
            "student_id": "STU-1002",
            "name": "Trần Thị B",
            "major": "Information Technology",
            "prior_gpa": 2.1,
            "attendance_rate": 0.65,
            "late_submissions_count": 5,
            "lms_activity_score": 42.0,
            "midterm_grade": 4.0
        }
    ],
    "intervention_logs": [
        {
            "log_id": "INT-3001",
            "student_id": "STU-1002",
            "intervention_type": "email_warning",
            "note": "Sent email warning due to attendance below 70%",
            "status": "Logged"
        }
    ]
}

DEFAULT_AGRICULTURE_STATE = {
    "services": {
        "iot_telemetry": {"status": "operational", "log": "Sensors logging telemetry every 15s."},
        "pest_classifier": {"status": "operational", "log": "PyTorch ResNet weights loaded on GPU."},
        "irrigation_relay": {"status": "degraded", "log": "Solenoid valve 4 disconnected since 02:00 AM."}
    },
    "farms": [
        {
            "farm_id": "FRM-501",
            "name": "Plot A - Durian",
            "crop_type": "Durian Monthong",
            "leaf_damage_percent": 8.2,
            "temperature": 28.5,
            "humidity": 78.0,
            "soil_moisture": 62.0,
            "days_since_last_treatment": 3
        },
        {
            "farm_id": "FRM-502",
            "name": "Plot B - Rice",
            "crop_type": "Rice ST25",
            "leaf_damage_percent": 45.0,
            "temperature": 33.5,
            "humidity": 45.0,
            "soil_moisture": 32.0,
            "days_since_last_treatment": 18
        }
    ],
    "treatment_logs": [
        {
            "log_id": "TRT-4001",
            "crop_id": "CRP-302",
            "treatment_type": "irrigation",
            "notes": "Emergency watering for drought stress",
            "status": "Applied"
        }
    ]
}

def _default_state_for_domain() -> Dict[str, Any]:
    domain = settings.ACTIVE_DOMAIN

    if domain == "education":
        default_state = DEFAULT_EDUCATION_STATE
    elif domain == "agriculture":
        default_state = DEFAULT_AGRICULTURE_STATE
    else:
        default_state = DEFAULT_SME_STATE

    return copy.deepcopy(default_state)

def _get_mongo_collection():
    if not settings.USE_MONGO or MongoClient is None:
        return None

    client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
    return client[settings.MONGO_DB_NAME]["domain_states"]

def get_storage_status() -> Dict[str, Any]:
    if not settings.USE_MONGO:
        return {
            "backend": "json_file",
            "mongo_enabled": False,
            "mongo_connected": False,
            "database": None,
            "collection": None,
        }

    try:
        collection = _get_mongo_collection()
        if collection is None:
            return {
                "backend": "json_file",
                "mongo_enabled": True,
                "mongo_connected": False,
                "database": None,
                "collection": None,
            }

        return {
            "backend": "mongo",
            "mongo_enabled": True,
            "mongo_connected": True,
            "database": settings.MONGO_DB_NAME,
            "collection": collection.name,
        }
    except PyMongoError as exc:
        return {
            "backend": "json_file",
            "mongo_enabled": True,
            "mongo_connected": False,
            "database": settings.MONGO_DB_NAME,
            "collection": "domain_states",
            "error": str(exc),
        }

def _load_db_from_file(default_state: Dict[str, Any]) -> Dict[str, Any]:
    db_file = settings.db_path

    if not os.path.exists(db_file):
        _save_db_to_file(default_state)
        return default_state
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_state

def _save_db_to_file(state: Dict[str, Any]):
    db_file = settings.db_path
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_db() -> Dict[str, Any]:
    default_state = _default_state_for_domain()
    domain = settings.ACTIVE_DOMAIN

    try:
        collection = _get_mongo_collection()
        if collection is None:
            return _load_db_from_file(default_state)

        doc = collection.find_one({"_id": domain})
        if not doc:
            save_db(default_state)
            return default_state

        return doc.get("state", default_state)
    except PyMongoError as exc:
        print(f"[DB] MongoDB unavailable, falling back to JSON file: {exc}")
        return _load_db_from_file(default_state)

def save_db(state: Dict[str, Any]):
    domain = settings.ACTIVE_DOMAIN

    try:
        collection = _get_mongo_collection()
        if collection is None:
            _save_db_to_file(state)
            return

        collection.update_one(
            {"_id": domain},
            {"$set": {"state": state}},
            upsert=True,
        )
    except PyMongoError as exc:
        print(f"[DB] MongoDB unavailable, falling back to JSON file: {exc}")
        _save_db_to_file(state)

def update_wallet(amount_change: int) -> int:
    db = load_db()
    if "wallet" not in db:
        db["wallet"] = {"balance": 1500000, "currency": "VND"}
    db["wallet"]["balance"] += amount_change
    save_db(db)
    return db["wallet"]["balance"]
