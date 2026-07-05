from typing import Dict, Any

class DiaryAgent:
    def log_diary(self, case_id: str | None = None) -> Dict[str, Any]:
        return {
            "case_saved": True,
            "reminder": "48h",
            "farm_log": "created"
        }
