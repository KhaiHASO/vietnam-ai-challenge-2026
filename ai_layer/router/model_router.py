from typing import Dict, Any, Tuple
from ai_layer.config import settings

class ModelRouter:
    def __init__(self):
        # Simulated fast cache for common FAQs to save API costs / local latency
        self.faq_cache = {
            "mở cửa lúc mấy giờ": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
            "giờ hoạt động": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
            "sân hoạt động lúc mấy giờ": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
            "hello": "Xin chào! Tôi có thể hỗ trợ gì cho bạn về đặt sân và chính sách dịch vụ?",
            "hi": "Xin chào! Tôi có thể hỗ trợ gì cho bạn về đặt sân và chính sách dịch vụ?"
        }

    def route_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Routes the user query.
        Returns:
            route_type (str): 'cache', 'faq_model', 'agent_model'
            metadata (dict): contains model recommended, cache data if hit, etc.
        """
        clean_query = query.strip().lower().rstrip("?").rstrip(".")
        
        # 1. Cache hit check
        if clean_query in self.faq_cache:
            return "cache", {
                "recommended_model": "local-cache",
                "cached_response": self.faq_cache[clean_query],
                "latency_estimate_ms": 1.0
            }
            
        # 2. Semantic routing by intent keywords (can be replaced by small LLM classifier)
        action_keywords = ["hủy", "cancel", "refund", "hoàn tiền", "đặt sân", "booking", "tạo ticket", "ticket", "service status", "kiểm tra"]
        
        is_action = any(kw in clean_query for kw in action_keywords)
        
        if is_action:
            # Requires complex reasoning (Agent model)
            return "agent_model", {
                "recommended_model": settings.MODEL_NAME,
                "provider": settings.PROVIDER,
                "reasoning_required": True,
                "requires_tools": True
            }
        else:
            # Standard conversational/FAQ question
            return "faq_model", {
                "recommended_model": settings.MODEL_NAME,
                "provider": settings.PROVIDER,
                "reasoning_required": False,
                "requires_tools": False
            }
        
    def add_cache(self, query: str, response: str):
        """Allows dynamically adding high-frequency responses to cache."""
        clean_query = query.strip().lower().rstrip("?").rstrip(".")
        self.faq_cache[clean_query] = response
