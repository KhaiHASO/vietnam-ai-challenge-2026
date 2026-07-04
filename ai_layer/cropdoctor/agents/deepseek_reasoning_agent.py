import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger("DeepSeekReasoningAgent")

MOCK_REASONING_DATABASE = {
    "Tomato___Early_blight": {
        "short_diagnosis": "Bệnh úa sớm (Early Blight) trên cây cà chua.",
        "top_possibilities": [
            "Bệnh úa sớm do nấm Alternaria solani (Khả năng 85% - Phù hợp với đốm đồng tâm trên lá già)",
            "Bệnh đốm lá Septoria (Khả năng 10% - Thường đốm nhỏ hơn, có nhụy xám)",
            "Bệnh mốc sương giai đoạn đầu (Khả năng 5% - Thường vết loang rộng hơn)"
        ],
        "why": [
            "Hình ảnh cho thấy các vết đốm màu nâu sẫm dạng vòng tròn đồng tâm đặc trưng của nấm Alternaria.",
            "Triệu chứng người dùng báo cáo trùng khớp với giai đoạn phát triển đầu tiên của bệnh úa sớm.",
            "Thường xuất hiện khi thời tiết chuyển mùa, nóng ẩm xen kẽ mưa rào."
        ],
        "questions_to_confirm": [
            "Các đốm bệnh này có xuất hiện nhiều nhất ở các lá già sát mặt đất trước không?",
            "Vết đốm có xuất hiện trên thân cây hoặc cuống quả dưới dạng đốm dài không?",
            "Bạn có tưới nước phun mưa trực tiếp lên lá vào chiều tối không?"
        ],
        "safe_recommendations": [
            "Tỉa bỏ ngay các lá già bị bệnh sát gốc và đem tiêu hủy xa khu vực trồng (không ủ phân hữu cơ).",
            "Tránh tưới nước trực tiếp lên lá, chuyển sang tưới dưới gốc và tưới vào buổi sáng để lá nhanh khô.",
            "Phun phòng bằng chế phẩm nấm đối kháng Trichoderma hoặc dịch tỏi/ớt nếu bệnh nhẹ.",
            "Nếu bệnh lây lan nhanh, có thể cân nhắc phun các hoạt chất sinh học bảo vệ thực vật được cấp phép như Bacillus subtilis."
        ],
        "when_to_call_expert": [
            "Khi hơn 30% diện tích lá trên toàn bộ vườn bị cháy xém.",
            "Khi xuất hiện vết thâm đen loang lổ trên quả làm rụng quả hàng loạt."
        ],
        "disclaimer": "Khuyến nghị này mang tính chất tham khảo dựa trên mô hình AI. Hãy tham khảo ý kiến cán bộ khuyến nông địa phương trước khi sử dụng các biện pháp hóa học liều lượng lớn."
    },
    "Tomato___Late_blight": {
        "short_diagnosis": "Bệnh mốc sương (Late Blight) nguy hiểm trên cây cà chua.",
        "top_possibilities": [
            "Bệnh mốc sương do noãn nấm Phytophthora infestans (Khả năng 90% - Nguy cơ lây lan cao)",
            "Bệnh úa sớm giai đoạn muộn (Khả năng 8% - Đốm thường khô hơn, ít tơ trắng)",
            "Tổn thương do sương muối hoặc bỏng lạnh (Khả năng 2%)"
        ],
        "why": [
            "Vết bệnh loang rộng như vết bỏng nước, mép vết bệnh màu nâu đen xám.",
            "Triệu chứng ẩm ướt kèm tơ trắng dưới mặt lá (nếu có) cực kỳ đặc trưng cho Phytophthora.",
            "Phát triển cực nhanh trong điều kiện trời mát mẻ (15-22°C) và độ ẩm không khí rất cao."
        ],
        "questions_to_confirm": [
            "Mặt dưới lá chỗ vết bệnh có xuất hiện lớp tơ mỏng màu trắng xám khi trời ẩm ướt không?",
            "Vết bệnh có lan sang thân cây làm thân bị thâm đen và dễ gãy gục không?",
            "Quả xanh có xuất hiện các vết loang lổ màu nâu đồng, bề mặt cứng ráp không?"
        ],
        "safe_recommendations": [
            "Thu gom triệt để và tiêu hủy ngay những cây bị bệnh nặng để ngăn chặn nguồn lây truyền bào tử nấm.",
            "Dừng ngay việc phun nước lên lá và bón phân đạm (phân hóa học nhiều nitơ).",
            "Tạo độ thông thoáng tối đa cho vườn cây bằng cách tỉa cành bấm ngọn hợp lý.",
            "Sử dụng các thuốc đặc trị nấm như Ridomil Gold hoặc các sản phẩm chứa gốc Metalaxyl/Mancozeb phun bao vây dập dịch nếu cần thiết."
        ],
        "when_to_call_expert": [
            "Bệnh xuất hiện đồng loạt trên diện rộng và lan sang các cây họ cà khác (như khoai tây).",
            "Cần can thiệp khẩn cấp từ cơ quan bảo vệ thực vật địa phương để tránh mất trắng."
        ],
        "disclaimer": "Bệnh mốc sương lây lan cực nhanh bằng gió và nước. Khuyến nghị mang tính tham khảo sơ bộ, cần hành động nhanh để bảo vệ vườn."
    },
    "Pepper,_bell___Bacterial_spot": {
        "short_diagnosis": "Bệnh đốm vi khuẩn (Bacterial Spot) trên cây ớt.",
        "top_possibilities": [
            "Bệnh đốm vi khuẩn do Xanthomonas campestris (Khả năng 85% - Phù hợp vết đốm nhỏ ngậm nước)",
            "Bệnh đốm lá do nấm Cercospora (Khả năng 10% - Đốm tròn hơn có tâm xám trắng)",
            "Bệnh thán thư giai đoạn đầu (Khả năng 5% - Thường tấn công quả nhiều hơn)"
        ],
        "why": [
            "Vết đốm nhỏ có màu vàng xanh sau chuyển nâu đen, hơi gồ lên ở mặt dưới lá.",
            "Bệnh phát triển mạnh sau các đợt mưa dông hoặc tưới phun áp lực mạnh làm bắn vi khuẩn từ đất lên."
        ],
        "questions_to_confirm": [
            "Các lá bị bệnh có hiện tượng vàng dần từ cuống rồi rụng hàng loạt không?",
            "Trên quả ớt có xuất hiện các đốm nhỏ màu nâu, trông giống như mụn cóc ráp không?",
            "Vườn có thường xuyên bị đọng nước hoặc độ ẩm luống đất quá cao không?"
        ],
        "safe_recommendations": [
            "Không đi vào vườn chăm sóc khi cây đang ướt để tránh vi khuẩn bám vào quần áo, công cụ lây lan.",
            "Nhổ bỏ các cây nhiễm bệnh nặng, dọn sạch cỏ dại xung quanh luống.",
            "Phun phòng bằng nước vôi trong pha loãng hoặc các chế phẩm đồng (Copper) sinh học.",
            "Hạn chế bón phân đạm hóa học, bổ sung Kali và Canxi để vách tế bào cây khỏe mạnh chống chịu vi khuẩn."
        ],
        "when_to_call_expert": [
            "Khi bệnh gây rụng lá hàng loạt trên 40% số cây trong vườn.",
            "Cần tư vấn giống kháng vi khuẩn cho vụ sau từ trạm giống nông nghiệp."
        ],
        "disclaimer": "Bệnh vi khuẩn khó chữa bằng thuốc hóa học thông thường. Ưu tiên phòng ngừa và vệ sinh vườn sạch sẽ."
    },
    "healthy": {
        "short_diagnosis": "Cây trồng khỏe mạnh, không phát hiện dấu hiệu bệnh lý nguy hiểm.",
        "top_possibilities": [
            "Lá cây phát triển bình thường, xanh tốt (Khả năng 95%)",
            "Thiếu vi lượng nhẹ hoặc căng thẳng sinh lý nhẹ do thời tiết (Khả năng 5%)"
        ],
        "why": [
            "Hình ảnh cho thấy phiến lá đều màu, không có vết đốm hoại tử, vết cháy hay lớp bào tử nấm.",
            "Cấu trúc lá nguyên vẹn, gân lá khỏe mạnh."
        ],
        "questions_to_confirm": [
            "Cây có ra hoa kết quả bình thường không?",
            "Hệ thống rễ và thân gốc có vững chắc, không bị thối đen hay héo rũ không?",
            "Lượng nước tưới và ánh sáng có được duy trì đều đặn hàng ngày không?"
        ],
        "safe_recommendations": [
            "Tiếp tục chế độ chăm sóc hiện tại, duy trì bón phân hữu cơ định kỳ để giữ đất tơi xốp.",
            "Tưới nước đều đặn vào buổi sáng, giữ gốc cây sạch cỏ dại.",
            "Theo dõi sát sao sau mỗi đợt mưa dông để phát hiện sớm các dấu hiệu sâu bệnh phát sinh."
        ],
        "when_to_call_expert": [
            "Khi cây bất ngờ bị héo rũ toàn thân vào ban ngày mặc dù đất vẫn đủ ẩm.",
            "Khi muốn lập lịch bón phân và chăm sóc tối ưu cho giai đoạn thu hoạch lớn."
        ],
        "disclaimer": "Kết quả chẩn đoán khỏe mạnh dựa trên phân tích hình ảnh lá. Hãy luôn theo dõi tổng thể sức khỏe của cả cây."
    }
}

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
                logger.warning(f"Failed to initialize OpenAI client: {e}. Will use fallback.")
                self.client = None

    def reason(self, vision_result: Dict[str, Any], symptoms: str = "", crop_hint: str = "") -> Dict[str, Any]:
        disease_label = vision_result.get("final_disease_label", "")
        decision_status = vision_result.get("decision_status", "uncertain")
        confidence = vision_result.get("confidence", 0.0)
        disease_vi = vision_result.get("final_disease_vi", "Không xác định")

        # Map decision status to diagnostic level
        diag_level = "low_confidence"
        if decision_status == "confident_preliminary_diagnosis":
            diag_level = "confident"
        elif decision_status == "need_more_symptoms":
            diag_level = "uncertain"

        # If API client is active and we have a key, call DeepSeek
        if self.client:
            try:
                logger.info("Calling DeepSeek API for Vietnamese reasoning analysis...")
                prompt = f"""
Bạn là chuyên gia nông nghiệp bảo vệ thực vật của ứng dụng CropDoctor AI.
Hãy phân tích kết quả từ mô hình thị giác máy tính và thông tin triệu chứng nông dân cung cấp để đưa ra chẩn đoán chính xác, lời khuyên an toàn (phòng trừ tổng hợp IPM) bằng tiếng Việt.

Thông tin đầu vào:
- Cây trồng nông dân báo cáo (crop_hint): {crop_hint}
- Triệu chứng nông dân mô tả thêm: {symptoms}
- Kết quả từ mô hình nhận dạng ảnh (Vision Consensus):
  + Tên bệnh gốc tiếng Anh: {disease_label}
  + Tên tiếng Việt sơ bộ: {disease_vi}
  + Độ tự tin của mô hình: {confidence * 100}%
  + Trạng thái chẩn đoán: {decision_status} (confident_preliminary_diagnosis: Tự tin, need_more_symptoms: Cần hỏi thêm triệu chứng, low_confidence_need_better_image_or_expert: Độ tự tin quá thấp)

Hãy phản hồi dưới dạng JSON hợp lệ duy nhất bằng tiếng Việt với cấu trúc sau (không kèm markdown ngoài khối json):
{{
  "diagnosis_level": "{diag_level}",
  "short_diagnosis": "Câu tóm tắt chẩn đoán ngắn gọn (Ví dụ: Bệnh úa sớm trên cây cà chua)",
  "top_possibilities": [
    "Khả năng 1 kèm phần trăm ước tính và lý do ngắn gọn",
    "Khả năng 2...",
    "Khả năng 3..."
  ],
  "why": [
    "Giải thích lý do 1 dựa vào hình ảnh hoặc triệu chứng",
    "Giải thích lý do 2..."
  ],
  "questions_to_confirm": [
    "Câu hỏi 1 để nông dân tự kiểm tra ruộng xác nhận bệnh (Ví dụ: Có đốm đồng tâm ở lá dưới không?)",
    "Câu hỏi 2...",
    "Câu hỏi 3..."
  ],
  "safe_recommendations": [
    "Biện pháp canh tác hoặc vệ sinh đồng ruộng 1",
    "Biện pháp sinh học hoặc phòng ngừa an toàn 2",
    "Biện pháp hóa học hợp lý 3 (chỉ nêu hoạt chất phổ biến được khuyên dùng, không quảng bá hãng thuốc cụ thể, nhấn mạnh an toàn)"
  ],
  "when_to_call_expert": [
    "Dấu hiệu 1 nên gọi chuyên gia/khuyến nông",
    "Dấu hiệu 2..."
  ],
  "disclaimer": "Lời miễn trừ trách nhiệm pháp lý chuẩn về nông nghiệp."
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
                # Clean markdown code blocks if the model wrapped it anyway
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Verify it is valid JSON
                parsed_json = json.loads(content)
                
                return {
                    "engine": "deepseek_reasoning_api",
                    "model": self.model,
                    "content": parsed_json,
                    "raw_response": content,
                    "fallback_used": False
                }
            except Exception as e:
                logger.error(f"DeepSeek API call failed: {e}. Falling back to local reasoning engine.")
                # fall through to mock

        # Local mock reasoning engine
        logger.info("Using local mock reasoning engine...")
        
        content_json = {
            "diagnosis_level": "low_confidence",
            "short_diagnosis": "Chẩn đoán chi tiết không khả dụng (Đang Ngoại tuyến / Chưa có API Key)",
            "top_possibilities": [
                "Chẩn đoán lập luận nông nghiệp bị tắt do chưa cấu hình DeepSeek API Key hoạt động."
            ],
            "why": [
                f"Lớp thị giác nhận diện sơ bộ lớp bệnh: '{disease_vi}' với độ tin cậy {round(confidence*100, 1)}%.",
                "Tuy nhiên, động cơ lập luận chuyên sâu (DeepSeek Reasoning Agent) hiện đang ngoại tuyến."
            ],
            "questions_to_confirm": [
                "Vui lòng cấu hình khóa DEEPSEEK_API_KEY hoạt động trong tệp .env để kích hoạt khả năng lập luận chuyên gia."
            ],
            "safe_recommendations": [
                "Nếu đây là trường hợp khẩn cấp thực tế, vui lòng liên hệ ngay với cán bộ khuyến nông hoặc trạm BVTV địa phương.",
                "Hãy chụp lại ảnh phiến lá thật cận cảnh, rõ nét, đủ ánh sáng và nằm trong danh sách cây trồng được hỗ trợ."
            ],
            "when_to_call_expert": [
                "Khi bệnh lan rộng làm rụng lá hàng loạt hoặc gây héo xanh đột ngột trên cây trồng."
            ],
            "disclaimer": "Tri thức lập luận nông nghiệp thời gian thực đòi hỏi kết nối đám mây hoạt động."
        }

        return {
            "engine": "deepseek_reasoning_local_offline",
            "model": "deepseek-local-offline-status",
            "content": content_json,
            "fallback_used": True,
            "note": "DeepSeek API key is missing or request failed. Mock templates have been disabled."
        }
