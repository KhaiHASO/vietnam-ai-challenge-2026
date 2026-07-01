import json
import os
from typing import Dict, Any, List

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_state.json")

DEFAULT_STATE = {
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

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_STATE)
        return DEFAULT_STATE
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STATE

def save_db(state: Dict[str, Any]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def update_wallet(amount_change: int) -> int:
    db = load_db()
    db["wallet"]["balance"] += amount_change
    save_db(db)
    return db["wallet"]["balance"]
