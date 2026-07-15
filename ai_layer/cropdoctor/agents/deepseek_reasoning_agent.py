import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger("DeepSeekReasoningAgent")


class DeepSeekReasoningAgent:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info(f"Initialized OpenAI client for DeepSeek reasoning with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}.")
                self.client = None

    def reason(self, vision_result: Dict[str, Any], symptoms: str = "", crop_hint: str = "", user_answers: str = "") -> Dict[str, Any]:
        disease_label = vision_result.get("final_disease_label", "")
        decision_status = vision_result.get("decision_status", "uncertain")
        confidence = vision_result.get("confidence", 0.0)
        disease_vi = vision_result.get("final_disease_vi", "Không xác định")

        diag_level = "low_confidence"
        if decision_status == "confident_preliminary_diagnosis":
            diag_level = "confident"
        elif decision_status == "need_more_symptoms":
            diag_level = "uncertain"

        if not self.client:
            raise RuntimeError("DeepSeek API client is not configured. Real analysis required, mock is disabled.")

        try:
            logger.info("Calling DeepSeek API for Vietnamese reasoning analysis...")
            prompt = f"""
Bạn là chuyên gia nông nghiệp bảo vệ thực vật của ứng dụng CropDoctor AI.
Nhiệm vụ của bạn là phân tích kết quả từ mô hình thị giác máy tính và thông tin triệu chứng do nông dân cung cấp.
QUAN TRỌNG: Không bao giờ được phép khẳng định chắc chắn 100% nếu vẫn còn thiếu thông tin (chưa trả lời các câu hỏi lâm sàng).

Thông tin đầu vào:
- Cây trồng nông dân báo cáo (crop_hint): {crop_hint}
- Triệu chứng ban đầu: {symptoms}
- Lời giải đáp các câu hỏi lâm sàng trước đó của nông dân (user_answers): {user_answers}
- Kết quả từ mô hình nhận dạng ảnh (Vision Consensus):
  + Tên bệnh gốc tiếng Anh: {disease_label}
  + Tên tiếng Việt sơ bộ: {disease_vi}
  + Độ tự tin của mô hình ảnh: {confidence * 100}%
  + Trạng thái chẩn đoán: {decision_status}

Nếu `user_answers` bị trống, hãy đưa ra 3 giả thuyết bệnh cạnh tranh nhau kèm theo % xác suất ước tính (tổng 100%), và đặt ra 2-3 câu hỏi cần thiết nhất (`questions_to_confirm`) để phân biệt chúng. 
Nếu `user_answers` có nội dung, hãy điều chỉnh lại % xác suất (tăng giảm tùy theo bằng chứng), và giải thích rõ trong phần `why` (Ví dụ: "Bệnh X tăng lên 71% vì vết bệnh không lõm").

Hãy phản hồi dưới dạng JSON hợp lệ duy nhất bằng tiếng Việt với cấu trúc sau:
{{
  "diagnosis_level": "{diag_level}",
  "short_diagnosis": "Câu tóm tắt chẩn đoán có điều kiện (Vd: Khả năng cao là... nhưng cần thêm bằng chứng)",
  "top_possibilities": ["Tên Bệnh 1: X% - Lý do ngắn gọn", "Tên Bệnh 2: Y% - Lý do", "Tên Bệnh 3: Z% - Lý do"],
  "evidence_for": ["Bằng chứng ủng hộ bệnh hàng đầu (Ví dụ: Từ ảnh, độ ẩm, triệu chứng)"],
  "evidence_against": ["Bằng chứng giúp chống lại/loại trừ các khả năng bệnh khác"],
  "why": ["Giải thích lý do cập nhật xác suất dựa trên user_answers hoặc hình ảnh"],
  "questions_to_confirm": ["Câu hỏi 1...", "Câu hỏi 2..."],
  "safe_recommendations": ["Biện pháp canh tác...", "Biện pháp sinh học..."],
  "ipm_plan": {{
    "immediate_actions": ["Hành động canh tác/vệ sinh ngay"],
    "monitoring_actions": ["Các bước theo dõi"],
    "expert_approval_actions": ["Các biện pháp can thiệp hóa học MẠNH cần chuyên gia duyệt"]
  }},
  "when_to_call_expert": ["Dấu hiệu 1...", "Dấu hiệu 2..."],
  "disclaimer": "Lời miễn trừ trách nhiệm pháp lý."
}}
"""
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful agricultural assistant. Output only a single valid JSON block without any markdown decorations or backticks, just the raw JSON text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            
            content = resp.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed_json = json.loads(content)
            
            return {
                "engine": "deepseek_reasoning_api",
                "model": self.model,
                "content": parsed_json,
                "raw_response": content,
                "fallback_used": False
            }
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}.")
            raise RuntimeError(f"DeepSeek reasoning execution failed: {e}") from e
