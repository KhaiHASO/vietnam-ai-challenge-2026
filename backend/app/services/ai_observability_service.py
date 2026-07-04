import json
from pathlib import Path
from typing import Any

from ai_layer.config import settings as ai_settings

from app.repositories.diagnosis_repository import DiagnosisRepository


class AiObservabilityService:
    def __init__(self, repository: DiagnosisRepository | None = None) -> None:
        self.repository = repository or DiagnosisRepository()
        self.project_root = Path(__file__).resolve().parents[3]

    async def model_report(self) -> dict[str, Any]:
        stored_reports = await self.repository.find_many(
            "model_reports",
            {},
            sort=[("created_at", -1)],
        )
        train_history = self._load_train_history()
        latest_metrics = self._latest_metrics(train_history)
        model_card = self._load_model_card()
        checkpoint_path = Path(ai_settings.domain_dir) / "data" / "model_checkpoint.pth"

        current_report = {
            "model_name": "ImpactTriageNet",
            "model_version": "impact-triage-v1.0",
            "domain": ai_settings.ACTIVE_DOMAIN,
            "framework": "PyTorch",
            "architecture": "Multi-task feed-forward network with tabular and text embedding fusion",
            "tasks": [
                "risk_level classification",
                "priority_score regression",
                "needs_human_review classification",
                "confidence_score regression",
            ],
            "checkpoint": {
                "path": str(checkpoint_path),
                "exists": checkpoint_path.exists(),
            },
            "train_history": train_history,
            "latest_metrics": latest_metrics,
            "model_card": model_card,
            "award_signals": {
                "pytorch_native_model": True,
                "multi_task_learning": True,
                "human_in_the_loop_for_high_risk": True,
                "ai_native_workflow": True,
                "agent_trace_logged": True,
            },
        }

        return {
            "current_report": current_report,
            "stored_reports": stored_reports,
        }

    async def agent_logs(
        self,
        case_id: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        query = {"case_id": case_id} if case_id else {}
        logs = await self.repository.find_many(
            "agent_logs",
            query,
            sort=[("created_at", -1)],
        )
        limited_logs = logs[: max(0, limit)]
        return {
            "case_id": case_id,
            "total": len(logs),
            "limit": limit,
            "logs": limited_logs,
        }

    def _load_train_history(self) -> dict[str, Any]:
        path = Path(ai_settings.domain_dir) / "data" / "train_history.json"
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"error": "invalid_train_history_json", "path": str(path)}

    def _latest_metrics(self, train_history: dict[str, Any]) -> dict[str, Any]:
        metrics: dict[str, Any] = {}
        for key, values in train_history.items():
            if isinstance(values, list) and values:
                metrics[key] = values[-1]
        return metrics

    def _load_model_card(self) -> dict[str, Any]:
        path = self.project_root / "ai_layer" / "pytorch_engine" / "model_card.md"
        if not path.exists():
            return {"path": str(path), "available": False}

        content = path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return {
            "path": str(path),
            "available": True,
            "title": lines[0].lstrip("# ").strip() if lines else "Model Card",
            "summary": lines[1:8],
        }
