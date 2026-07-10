import logging
from typing import List

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Rule engine đơn giản để áp dụng các luật xử lý (pre/post processing) 
    lên câu hỏi hoặc câu trả lời.
    """
    
    def __init__(self, block_keywords: List[str] = None):
        self.block_keywords = block_keywords or ["bạo lực", "hack", "lừa đảo"]
        
    def pre_process_query(self, query: str) -> str:
        """Kiểm tra câu hỏi trước khi đưa vào hệ thống."""
        query_lower = query.lower()
        for kw in self.block_keywords:
            if kw in query_lower:
                logger.warning(f"Blocked query due to keyword: {kw}")
                raise ValueError("Truy vấn của bạn vi phạm chính sách nội dung của hệ thống.")
        return query

    def post_process_answer(self, answer: str, domain: str) -> str:
        """Thêm các thông tin cảnh báo pháp lý tùy thuộc vào domain."""
        disclaimer = ""
        if domain == "agriculture":
            disclaimer = "\n\n*Lưu ý: Đây là tư vấn từ Trợ lý ảo AI. Vui lòng tham khảo thêm ý kiến chuyên gia nông nghiệp hoặc kiểm tra thực tế trước khi áp dụng.*"
        elif domain == "healthcare":
            disclaimer = "\n\n*Lưu ý pháp lý: Đây chỉ là tư vấn tham khảo từ AI. Không được sử dụng thay thế cho chẩn đoán của bác sĩ. Vui lòng đến bệnh viện để được tư vấn y tế chính xác.*"
            
        return answer + disclaimer
