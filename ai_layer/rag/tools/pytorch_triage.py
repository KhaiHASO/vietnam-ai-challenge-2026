import logging
from ai_layer.rag.contracts.events import ModelSignal, RiskLevel
from ai_layer.pytorch_engine.inference import predict_triage

logger = logging.getLogger(__name__)

class PyTorchTriage:
    async def analyze(self, query: str, metadata: dict | None = None, domain: str = "agriculture") -> ModelSignal:
        meta = metadata or {}
        try:
            res = predict_triage(query, meta, domain)
            
            risk_str = res.get("risk_level", "low").lower()
            if risk_str == "high":
                risk = RiskLevel.HIGH
            elif risk_str == "medium":
                risk = RiskLevel.MEDIUM
            else:
                risk = RiskLevel.LOW

            engine = res.get("engine", "")
            if "fallback" in engine.lower() or "rule" in engine.lower():
                engine_status = "fallback"
            else:
                engine_status = "ok"

            return ModelSignal(
                risk_level=risk,
                priority=float(res.get("priority", 0.0)),
                requires_review=bool(res.get("needs_human_review", False)),
                confidence=float(res.get("confidence", 0.0)),
                model_version=res.get("model_version", "unknown"),
                latency_ms=15.0,
                engine_status=engine_status
            )
        except Exception as e:
            logger.warning(f"Error during predict_triage: {e}. Returning fallback signal.")
            return ModelSignal(
                risk_level=RiskLevel.LOW,
                priority=0.3,
                requires_review=False,
                confidence=0.5,
                model_version="fallback-heuristics-v1.0",
                latency_ms=1.0,
                engine_status="fallback"
            )
