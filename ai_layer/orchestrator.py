import time
import re
from typing import Dict, Any, List
from ai_layer.config import settings
from ai_layer.guardrails.pii import PIIScanner
from ai_layer.guardrails.input_safety import InputSafetyGuardrail
from ai_layer.guardrails.output_safety import OutputSafetyGuardrail
from ai_layer.router.model_router import ModelRouter
from ai_layer.rag.vector_db import LocalVectorDB
from ai_layer.agents.planner import AgentPlanner
from ai_layer.approval.hitl import hitl_manager
from ai_layer.pytorch_engine.inference import predict_triage

class AIOrchestrator:
    def __init__(self):
        self.pii_scanner = PIIScanner()
        self.input_guardrail = InputSafetyGuardrail()
        self.output_guardrail = OutputSafetyGuardrail()
        self.router = ModelRouter()
        self.vector_db = LocalVectorDB()
        self.planner = AgentPlanner()

    def _extract_metadata_from_query(self, query: str) -> dict:
        lower = query.lower()
        meta = {}
        
        meta["leaf_damage_percent"] = 45.0 if any(w in lower for w in ["sâu bệnh", "đốm nâu", "rầy nâu", "hại", "lá vàng"]) else 5.0
        meta["temperature"] = 34.0 if any(w in lower for w in ["nóng", "nắng", "nhiệt độ"]) else 28.0
        meta["humidity"] = 42.0 if any(w in lower for w in ["khô", "ẩm", "độ ẩm"]) else 75.0
        meta["soil_moisture"] = 35.0 if any(w in lower for w in ["hạn", "nước", "tưới"]) else 65.0
        meta["days_since_last_treatment"] = 18.0 if any(w in lower for w in ["lâu", "ngày", "trước"]) else 3.0
            
        return meta

    def process_request(self, user_query: str) -> Dict[str, Any]:
        """
        Executes the 9-step AI-Native Architecture pipeline dynamically.
        """
        start_time = time.time()
        telemetry = {}
        domain = settings.ACTIVE_DOMAIN
        
        # Step 1: PII Scan
        step_start = time.time()
        redacted_query, pii_mapping = self.pii_scanner.scan_and_redact(user_query)
        telemetry["step_1_pii"] = {
            "name": "Input Capture & PII Scan",
            "original_query": user_query,
            "redacted_query": redacted_query,
            "pii_detected": len(pii_mapping) > 0,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        # Step 2: Input Safety Guardrail
        step_start = time.time()
        is_blocked, risk_score, safety_reason = self.input_guardrail.evaluate_safety(redacted_query)
        telemetry["step_2_input_safety"] = {
            "name": "Input Safety Guardrail",
            "is_blocked": is_blocked,
            "risk_score": risk_score,
            "reason": safety_reason,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        if is_blocked:
            total_duration = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response": "Yêu cầu của bạn bị từ chối do vi phạm quy định an toàn hệ thống (Prompt Injection / Disallowed commands).",
                "telemetry": telemetry,
                "duration_ms": total_duration,
                "blocked": True
            }
            
        # Step 3: Semantic Model Router
        step_start = time.time()
        route_type, router_meta = self.router.route_query(redacted_query)
        telemetry["step_3_router"] = {
            "name": "Semantic Model Router",
            "route": route_type,
            "metadata": router_meta,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        # Step 4: RAG / Vector Search
        step_start = time.time()
        rag_results = self.vector_db.search(redacted_query, top_k=2)
        retrieved_texts = [doc["content"] for doc, score in rag_results]
        telemetry["step_4_rag"] = {
            "name": "CUDA Vector Search - RAG",
            "docs_found": len(rag_results),
            "retrieved": [{"id": doc["id"], "score": score} for doc, score in rag_results],
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        # Step 4.5: PyTorch Impact Triage Engine
        step_start = time.time()
        metadata = self._extract_metadata_from_query(redacted_query)
        pytorch_res = predict_triage(redacted_query, metadata)
        telemetry["pytorch_engine"] = {
            "name": "PyTorch Impact Triage Engine",
            "results": pytorch_res,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        # Step 7: Human-in-the-Loop Approval check
        is_hitl_triggered = False
        hitl_approval_id = None
        final_response = ""
        
        # Logic to trigger HITL based on PyTorch predictions (Agriculture only)
        is_high_risk = any(w in redacted_query.lower() for w in ["hóa chất", "thuốc trừ sâu", "phun thuốc"]) or pytorch_res.get("needs_human_review", False)

        if is_high_risk:
            is_hitl_triggered = True
            
            action_type = "chemical_pesticide_approval"
            details = {
                "crop_id": "CRP-304",
                "chemical": "Fungicide NPK-II",
                "user_query": redacted_query,
                "risk_level": pytorch_res["risk_level"],
                "priority": pytorch_res["priority"]
            }
            final_response = f"Khuyến nghị phun thuốc hóa chất trị nấm cho vườn sầu riêng (Mã CRP-304) đang chờ chuyên gia phê duyệt để đảm bảo an toàn sinh học môi trường."
                
            approval_id = hitl_manager.create_pending_approval(
                action_type=action_type,
                details=details
            )
            hitl_approval_id = approval_id
            
            telemetry["step_5_planner"] = {"name": "Agent Planner", "skipped": True, "reason": "HITL Intercept"}
            telemetry["step_6_executor"] = {"name": "Tool Executor", "skipped": True}
            telemetry["step_7_hitl"] = {
                "name": "Human-in-the-Loop",
                "triggered": True,
                "approval_id": approval_id,
                "status": "Pending Approval",
                "duration_ms": 0.0
            }
            
        elif route_type == "cache":
            final_response = router_meta["cached_response"]
            telemetry["step_5_planner"] = {"name": "Agent Planner", "route": "cache_hit"}
            telemetry["step_6_executor"] = {"name": "Tool Executor", "route": "cache_hit"}
            telemetry["step_7_hitl"] = {"name": "Human-in-the-Loop", "triggered": False}
            
        else: # faq_model or agent_model
            # Step 5 & 6: Agent planning and execution
            step_start = time.time()
            final_response, agent_steps = self.planner.plan_and_execute(redacted_query, retrieved_texts)
            
            telemetry["step_5_planner"] = {
                "name": "Agent Planner",
                "steps": agent_steps,
                "duration_ms": (time.time() - step_start) * 1000
            }
            telemetry["step_6_executor"] = {
                "name": "Tool Executor",
                "status": "Completed",
                "duration_ms": 0.0
            }
            telemetry["step_7_hitl"] = {
                "name": "Human-in-the-Loop",
                "triggered": False
            }
            
        # Step 8: Output Guardrail
        step_start = time.time()
        output_blocked, hallucination_score, output_reason = self.output_guardrail.evaluate_output(
            final_response, retrieved_texts
        )
        telemetry["step_8_output_safety"] = {
            "name": "Output Guardrail Check",
            "is_blocked": output_blocked,
            "hallucination_score": hallucination_score,
            "reason": output_reason,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        if output_blocked and not is_hitl_triggered:
            final_response = "Tôi xin lỗi, câu trả lời đang gặp vấn đề xác thực thông tin. Vui lòng thử lại sau."
            
        # Restore PII details
        final_response = self.pii_scanner.restore_pii(final_response, pii_mapping)
        
        # Step 9: Smart Response Dispatcher
        step_start = time.time()
        total_duration = (time.time() - start_time) * 1000
        telemetry["step_9_dispatcher"] = {
            "name": "Smart Response Dispatcher",
            "status": "Success",
            "total_duration_ms": total_duration,
            "duration_ms": (time.time() - step_start) * 1000
        }
        
        return {
            "success": True,
            "response": final_response,
            "telemetry": telemetry,
            "duration_ms": total_duration,
            "hitl_triggered": is_hitl_triggered,
            "hitl_approval_id": hitl_approval_id,
            "pytorch_triage": pytorch_res
        }
