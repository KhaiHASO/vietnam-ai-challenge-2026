# Specifications: Đặc Tả Kỹ Thuật Luồng Chẩn Đoán Lâm Sàng CropDoctor AI

Tài liệu đặc tả các giao thức API đầu vào và đầu ra để hỗ trợ các tính năng sát thủ mới.

## 1. Giao thức chẩn đoán có từ chối ảnh (`POST /api/cropdoctor/diagnose`)

### Phân tích chất lượng ảnh (PIL & Numpy)
- Nếu độ sáng trung bình của ảnh $< 45$ (trên thang 255): Đánh dấu `status = "invalid"`, `issues = ["too_dark"]`.
- Nếu độ lệch chuẩn màu xám (contrast/sharpness) $< 15$: Đánh dấu `status = "invalid"`, `issues = ["blurry_or_low_contrast"]`.

### Trả về khi từ chối ảnh
```json
{
  "status": "success",
  "vision": {
    "decision_status": "low_confidence_need_better_image_or_expert",
    "final_disease_label": "Unknown",
    "final_disease_vi": "Ảnh không đạt chất lượng (quá mờ hoặc quá tối)",
    "confidence": 0.0,
    "primary_engine": "image_quality_guardrail",
    "notes": ["blurry_or_low_contrast"]
  },
  "reasoning": {
    "content": {
      "diagnosis_level": "low_confidence",
      "short_diagnosis": "Không thể chẩn đoán do ảnh bị mờ hoặc tối",
      "top_possibilities": ["Ảnh chụp thiếu chi tiết hoặc ngược sáng"],
      "why": ["Hệ thống phát hiện độ sắc nét hoặc độ sáng không đạt tiêu chuẩn lâm sàng."],
      "questions_to_confirm": ["Vui lòng chụp lại ảnh rõ nét mặt trên của lá và đủ ánh sáng."],
      "safe_recommendations": ["Di chuyển điện thoại song song với phiến lá, giữ khoảng cách 15-20cm, chụp ngoài trời sáng."],
      "when_to_call_expert": ["Nếu không thể chụp được ảnh rõ nét, vui lòng gửi mẫu trực tiếp cho trạm bảo vệ thực vật."]
    }
  }
}
```

## 2. Đặc tả chẩn đoán phân biệt & kế hoạch IPM an toàn
Trong `reasoning.content` trả về:
- `evidence_for`: Lý do ủng hộ chẩn đoán hàng đầu.
- `evidence_against`: Lý do loại bỏ các giả thuyết khác.
- `ipm_plan`: IPM 3 tầng:
  - `immediate_actions`: Hành động không hóa chất làm ngay.
  - `monitoring_actions`: Theo dõi & lấy thêm mẫu.
  - `expert_approval_actions`: Hoạt chất hóa học mạnh cần phê duyệt.

## 3. Giao thức vòng lặp 48 giờ (`POST /api/diagnosis/cases/{case_id}/follow-up`)
Nông dân gửi ảnh mới lên để đối chiếu:
- Request: `{"image_id": "img_new", "notes": "Đã tỉa lá bệnh"}`
- Response: So sánh mức độ tổn thương của ảnh cũ và ảnh mới (ví dụ giảm từ 18% xuống 5%).
