import time
from typing import Dict, Any, List
from ai_layer.guardrails.pii import PIIScanner
from ai_layer.guardrails.input_safety import InputSafetyGuardrail
from ai_layer.guardrails.output_safety import OutputSafetyGuardrail
from ai_layer.router.model_router import ModelRouter
from ai_layer.rag.vector_db import LocalVectorDB
from ai_layer.agents.planner import AgentPlanner
from ai_layer.approval.hitl import hitl_manager

class AIOrchestrator:
    def __init__(self):
        self.pii_scanner = PIIScanner()
        self.input_guardrail = InputSafetyGuardrail()
        self.output_guardrail = OutputSafetyGuardrail()
        self.router = ModelRouter()
        self.vector_db = LocalVectorDB()
        self.planner = AgentPlanner()

    def process_request(self, user_query: str) -> Dict[str, Any]:
        """
        Executes the 9-step AI-Native Architecture pipeline.
        Returns:
            Dict containing final response, trace steps telemetry, execution stats.
        """
        start_time = time.time()
        telemetry = {}
        trace_steps = []
        
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
        
        # Determine how to handle routing
        final_response = ""
        agent_steps = []
        is_hitl_triggered = False
        hitl_approval_id = None
        
        # Intercept High-Risk actions before sending to planner (e.g. canceling or refunding money)
        # In a production AI-Native cockpit, we guard high-risk intent proactively
        is_high_risk_intent = any(w in redacted_query.lower() for w in ["hủy sân", "hủy đặt sân", "refund", "hoàn tiền"])
        
        if is_high_risk_intent:
            is_hitl_triggered = True
            # Create a pending approval
            booking_id = "BKG-88321A"  # Default mock or parsed from query
            approval_id = hitl_manager.create_pending_approval(
                action_type="cancel_booking_refund",
                details={
                    "booking_id": booking_id,
                    "refund_amount": 220000,
                    "user_query": redacted_query
                }
            )
            hitl_approval_id = approval_id
            final_response = f"Yêu cầu hủy sân và hoàn tiền cho mã đặt chỗ {booking_id} của bạn đã được ghi nhận. Do đây là giao dịch ảnh hưởng tài chính, hệ thống đã chuyển tiếp yêu cầu đến Quản trị viên để phê duyệt thủ công (Mã yêu cầu: {approval_id})."
            
            telemetry["step_5_planner"] = {
                "name": "Agent Planner",
                "skipped": True,
                "reason": "Intercepted due to High Risk intent"
            }
            telemetry["step_6_executor"] = {
                "name": "Tool Executor",
                "skipped": True
            }
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
            
        # Restore PII details if any were redacted, so the final response looks personalized to the user
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
            "hitl_approval_id": hitl_approval_id
        }
