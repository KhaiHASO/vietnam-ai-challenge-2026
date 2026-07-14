import os
import json
from typing import Dict, Any, Tuple
from ai_layer.config import settings

class ModelRouter:
    def __init__(self, domain_id: str = "agriculture"):
        self.domain_id = domain_id
        # Default FAQ caches for each domain
        self.default_caches = {
            "sme": {
                "mở cửa lúc mấy giờ": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
                "giờ hoạt động": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
                "sân hoạt động lúc mấy giờ": "Hệ thống sân hoạt động từ 6:00 đến 22:00 hàng ngày.",
                "hello": "Xin chào! Tôi là trợ lý vận hành SME. Tôi có thể hỗ trợ gì cho bạn?",
                "hi": "Xin chào! Tôi là trợ lý vận hành SME. Tôi có thể hỗ trợ gì cho bạn?"
            },
            "education": {
                "điều kiện nhận học bổng": "Sinh viên cần đạt GPA tối thiểu 3.6/4.0 và điểm rèn luyện đạt loại Xuất sắc (trên 90 điểm) để xét học bổng.",
                "lịch thi kì này": "Lịch thi học kỳ sẽ được công bố vào tuần 12 của học kỳ trên cổng thông tin sinh viên.",
                "hello": "Xin chào! Tôi là trợ lý hỗ trợ sinh viên học vụ. Tôi có thể giúp gì cho bạn?",
                "hi": "Xin chào! Tôi là trợ lý hỗ trợ sinh viên học vụ. Tôi có thể giúp gì cho bạn?"
            },
            "agriculture": {
                "quy định tưới nước tiêu chuẩn": "Thời gian tưới nước tiêu chuẩn là 6:00 sáng và 5:00 chiều hàng ngày. Lượng nước 15 lít/gốc cho cây ăn quả.",
                "khi nào phun thuốc trừ sâu": "Chỉ phun thuốc khi mật độ sâu hại vượt ngưỡng kinh tế (ví dụ: trên 5 con/m2 đối với rầy nâu).",
                "hello": "Xin chào! Tôi là trợ lý giám sát nông nghiệp thông minh. Tôi có thể giúp gì cho bạn?",
                "hi": "Xin chào! Tôi là trợ lý giám sát nông nghiệp thông minh. Tôi có thể giúp gì cho bạn?"
            }
        }
        
        # Default action keywords for each domain
        self.action_keywords = {
            "sme": ["hủy", "cancel", "refund", "hoàn tiền", "đặt sân", "booking", "tạo ticket", "ticket", "service status", "kiểm tra"],
            "education": ["cảnh báo", "học bổng", "can thiệp", "rớt môn", "nguy cơ", "dropout", "log", "grades", "sinh viên", "điểm"],
            "agriculture": ["sâu bệnh", "phun thuốc", "lá vàng", "treatment", "điều trị", "farm", "hóa chất", "bón phân", "pest"]
        }

    def _get_faq_cache(self) -> Dict[str, str]:
        # Try loading from local domain file if it exists
        domain = self.domain_id
        faq_file = settings.data_path(domain) / "faq_cache.json"
        if os.path.exists(faq_file):
            try:
                with open(faq_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self.default_caches.get(domain, self.default_caches["sme"])

    def route_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Routes the user query dynamically based on active domain.
        """
        clean_query = query.strip().lower().rstrip("?").rstrip(".")
        faq_cache = self._get_faq_cache()
        
        # 1. Cache hit check
        if clean_query in faq_cache:
            return "cache", {
                "recommended_model": "local-cache",
                "cached_response": faq_cache[clean_query],
                "latency_estimate_ms": 1.0
            }
            
        # 2. Semantic routing by intent keywords
        domain = self.domain_id
        keywords = self.action_keywords.get(domain, self.action_keywords["sme"])
        is_action = any(kw in clean_query for kw in keywords)
        
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
        # This saves to the active cache in-memory, but we can also write to the file
        clean_query = query.strip().lower().rstrip("?").rstrip(".")
        domain = self.domain_id
        if domain not in self.default_caches:
            self.default_caches[domain] = {}
        self.default_caches[domain][clean_query] = response
        
        # Try saving to file
        faq_file = settings.data_path(domain) / "faq_cache.json"
        os.makedirs(os.path.dirname(faq_file), exist_ok=True)
        try:
            faq_cache = self._get_faq_cache()
            faq_cache[clean_query] = response
            with open(faq_file, "w", encoding="utf-8") as f:
                json.dump(faq_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
