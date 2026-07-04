Dựa trên UI hiện có trong file screenshot: hệ thống đã có đủ các route quan trọng như **Tổng quan, Chẩn đoán mới, Lịch sử chẩn đoán, Ca cần theo dõi, Quản lý vườn, Nhật ký mùa vụ, Lịch nhắc, Thư viện bệnh cây, Khuyến nghị IPM, Bản đồ ca bệnh, Chuyên gia xác nhận, Model PyTorch, Nhật ký Agent**. Vì vậy team FE **không nên vẽ thêm màn mới**, chỉ cần gắn API đúng dữ liệu vào các màn này. 

# Phân chia nhiệm vụ chuẩn cho demo CropDoctor AI

## Tư duy chia việc

Team AI chịu trách nhiệm:

```text
Ảnh cây bệnh → phân tích AI → hỏi triệu chứng → suy luận → khuyến nghị → log agent → báo cáo model
```

Team BE chịu trách nhiệm:

```text
Lưu dữ liệu → điều phối workflow → cung cấp API cho FE → quản lý case → nhật ký → nhắc lịch → dashboard → chuyên gia xác nhận
```

Team FE hiện đã có giao diện, nên chỉ cần:

```text
Gọi API → render dữ liệu → upload ảnh → hiển thị trạng thái → nối luồng demo
```

---

# 1. Luồng demo chính cần bám sát

Luồng thắng giải nên chạy như sau:

```text
Dashboard tổng quan
→ Chẩn đoán mới
→ Chọn cây/vườn
→ Upload ảnh
→ AI Vision phân tích
→ Agent hỏi triệu chứng
→ Kết luận chẩn đoán
→ Kế hoạch xử lý an toàn
→ Tự lưu nhật ký mùa vụ
→ Tự tạo lịch nhắc 48h
→ Case xuất hiện ở Ca cần theo dõi
→ Case xuất hiện ở Dashboard hợp tác xã / bản đồ
→ Nhật ký Agent ghi rõ từng bước AI đã chạy
→ Model PyTorch report chứng minh kỹ thuật
```

Đây là xương sống. Mọi nhiệm vụ AI/BE phải phục vụ luồng này, không làm lan man.

---

# 2. Team AI cần làm gì?

## AI-01. Vision Model chẩn đoán bệnh từ ảnh

### Mục tiêu

Nhận ảnh lá/thân/quả, trả về top bệnh nghi ngờ, độ tin cậy, chất lượng ảnh và vùng nghi bệnh.

### Input

```json
{
  "case_id": "CASE-2026-0704-001",
  "crop_type": "Ớt",
  "growth_stage": "Ra hoa",
  "image_url": "/uploads/cases/CASE-001/leaf.jpg"
}
```

### Output bắt buộc

```json
{
  "image_quality": {
    "score": 0.91,
    "status": "good",
    "message": "Ảnh đạt yêu cầu, có thể phân tích."
  },
  "predictions": [
    {
      "disease_code": "anthracnose_chili",
      "disease_name": "Thán thư trên ớt",
      "confidence": 0.74
    },
    {
      "disease_code": "bacterial_spot",
      "disease_name": "Đốm lá vi khuẩn",
      "confidence": 0.16
    },
    {
      "disease_code": "chemical_burn",
      "disease_name": "Cháy lá do thuốc",
      "confidence": 0.07
    }
  ],
  "explainability": {
    "heatmap_url": "/ai-results/CASE-001/gradcam.jpg",
    "lesion_count": 14,
    "leaf_area_affected": 0.18
  },
  "need_more_questions": true
}
```

### Việc cụ thể team AI làm

```text
- Fine-tune hoặc dùng model có sẵn bằng PyTorch.
- Ưu tiên EfficientNet-B0 / MobileNetV3 / ResNet18 cho nhẹ, dễ demo.
- Dataset demo: PlantVillage + PlantDoc + ảnh seed tự chuẩn bị.
- Export inference service.
- Tạo Grad-CAM hoặc fake Grad-CAM ổn định cho demo.
- Trả về top-3 bệnh + confidence.
- Có kiểm tra chất lượng ảnh: mờ, thiếu sáng, không thấy lá.
```

### Màn FE sử dụng

```text
Màn 4: AI Vision phân tích ảnh
Màn 12: Model PyTorch Report
Màn 13: Nhật ký Agent
```

---

## AI-02. Symptom Agent hỏi thêm triệu chứng

### Mục tiêu

Không kết luận ngay sau ảnh. AI phải biết hỏi thêm để phân biệt bệnh.

### Input

```json
{
  "case_id": "CASE-2026-0704-001",
  "crop_type": "Ớt",
  "vision_predictions": [
    "Thán thư trên ớt",
    "Đốm lá vi khuẩn",
    "Cháy lá do thuốc"
  ]
}
```

### Output

```json
{
  "questions": [
    {
      "id": "q1",
      "question": "Đốm bệnh xuất hiện sau mưa hay sau khi phun thuốc?",
      "type": "single_choice",
      "options": ["Sau mưa", "Sau phun thuốc", "Không rõ"]
    },
    {
      "id": "q2",
      "question": "Bệnh xuất hiện nhiều ở lá già hay lá non?",
      "type": "single_choice",
      "options": ["Lá già", "Lá non", "Cả hai"]
    },
    {
      "id": "q3",
      "question": "Bệnh có lan sang cây bên cạnh không?",
      "type": "single_choice",
      "options": ["Có", "Không", "Chưa kiểm tra"]
    }
  ]
}
```

### Việc cụ thể team AI làm

```text
- Xây bộ câu hỏi theo từng nhóm bệnh.
- Với demo, không cần LLM quá phức tạp.
- Làm rule-based + prompt LLM đều được.
- Quan trọng là câu hỏi phải phục vụ chẩn đoán phân biệt.
- Mỗi case nên hỏi 3–5 câu là đủ.
```

### Màn FE sử dụng

```text
Màn 5: Chat hỏi thêm triệu chứng
Màn 13: Nhật ký Agent
```

---

## AI-03. Context Agent lấy bối cảnh canh tác

### Mục tiêu

AI không chỉ nhìn ảnh, mà còn dùng bối cảnh: cây gì, vườn nào, giai đoạn nào, mưa gần đây, nhật ký chăm sóc.

### Input

```json
{
  "case_id": "CASE-2026-0704-001",
  "farm": {
    "name": "Vườn ớt Trảng Bom",
    "location": "Trảng Bom, Đồng Nai",
    "crop_type": "Ớt",
    "growth_stage": "Ra hoa"
  },
  "recent_logs": [
    "03/07/2026: Tỉa lá bệnh, giảm tưới 30%",
    "01/07/2026: Tưới nhỏ giọt 45 phút"
  ],
  "weather": {
    "rain_after_days": 3,
    "humidity": 89,
    "rainfall_mm": 42
  }
}
```

### Output

```json
{
  "context_summary": "Trảng Bom có mưa liên tục 3 ngày, độ ẩm 85–92%, chưa ghi nhận phun thuốc trong 7 ngày.",
  "context_features": {
    "rain_after": "3_days",
    "humidity": 0.89,
    "spray_gap_days": 7,
    "growth_stage": "flowering"
  }
}
```

### Việc cụ thể team AI làm

```text
- Nhận dữ liệu từ BE, không tự quản lý database.
- Tóm tắt bối cảnh ngắn gọn.
- Trích xuất feature cho Reasoning Agent.
- Với demo, thời tiết có thể mock theo Đồng Nai.
```

### Màn FE sử dụng

```text
Màn 6: Kết luận chẩn đoán
Màn 13: Nhật ký Agent
```

---

## AI-04. Reasoning Agent kết luận chẩn đoán

### Mục tiêu

Tổng hợp ảnh + triệu chứng + bối cảnh để đưa ra kết luận cuối.

### Input

```json
{
  "vision_result": {
    "top_prediction": "Thán thư trên ớt",
    "confidence": 0.74
  },
  "symptoms": {
    "appeared_after": "Sau mưa",
    "leaf_age": "Lá già",
    "spread": "Có, nhưng ít"
  },
  "context": {
    "humidity": 0.89,
    "rain_after": "3_days",
    "spray_gap_days": 7
  }
}
```

### Output

```json
{
  "final_diagnosis": {
    "disease_code": "anthracnose_chili",
    "disease_name": "Thán thư trên ớt",
    "confidence": 0.89,
    "severity": "medium"
  },
  "differential_diagnosis": [
    "Đốm lá vi khuẩn",
    "Cháy lá do thuốc",
    "Thiếu kali"
  ],
  "reasoning": [
    "Ảnh có đốm nâu lõm ở tâm, viền vàng nhạt.",
    "Bệnh xuất hiện sau mưa.",
    "Bắt đầu từ lá già.",
    "Độ ẩm khu vực gần đây cao.",
    "Không có ghi nhận phun thuốc trong 7 ngày nên giảm khả năng cháy lá do thuốc."
  ],
  "expert_required": false
}
```

### Việc cụ thể team AI làm

```text
- Làm scoring lại confidence sau khi có triệu chứng.
- Tạo phần “Lý do AI kết luận”.
- Luôn có chẩn đoán phân biệt.
- Có cờ expert_required nếu confidence thấp hoặc bệnh nghiêm trọng.
```

### Logic đề xuất

```text
Nếu confidence >= 0.8 → AI kết luận, theo dõi.
Nếu 0.6 <= confidence < 0.8 → cần chụp lại / hỏi thêm / theo dõi.
Nếu confidence < 0.6 → chuyển chuyên gia xác nhận.
Nếu severity = high hoặc lan rộng nhanh → chuyển chuyên gia.
```

---

## AI-05. Safety/IPM Agent khuyến nghị xử lý an toàn

### Mục tiêu

Đưa ra kế hoạch xử lý nhưng không phán bừa thuốc BVTV.

### Output

```json
{
  "treatment_plan": {
    "immediate_actions": [
      "Tỉa bỏ lá bệnh nặng và tiêu hủy xa vườn.",
      "Không tưới lên lá vào chiều tối.",
      "Tăng thông thoáng luống."
    ],
    "monitoring": [
      "Chụp lại ảnh sau 48 giờ.",
      "Kiểm tra mặt dưới lá.",
      "Đánh dấu cây bị bệnh để theo dõi lan rộng."
    ],
    "escalation": [
      "Nếu bệnh lan nhanh, liên hệ cán bộ nông nghiệp hoặc chuyên gia.",
      "Khi dùng thuốc BVTV cần tuân thủ nguyên tắc 4 đúng."
    ],
    "safety_warning": "Không khuyến nghị phun thuốc ngay nếu bệnh chưa lan rộng. Ưu tiên IPM và theo dõi sau 48 giờ."
  }
}
```

### Việc cụ thể team AI làm

```text
- Xây knowledge base IPM cho từng nhóm bệnh.
- Không tự ghi tên thuốc cụ thể nếu chưa có nguồn pháp lý chắc.
- Khuyến nghị theo 3 tầng: làm ngay, theo dõi, chuyển chuyên gia.
- Sinh cảnh báo an toàn.
```

### Màn FE sử dụng

```text
Màn 7: Kế hoạch xử lý an toàn
Màn 9: Khuyến nghị IPM
```

---

## AI-06. Follow-up Agent tạo nhắc lịch

### Mục tiêu

Sau khi chẩn đoán, AI tự đề xuất lịch nhắc.

### Output

```json
{
  "reminders": [
    {
      "title": "Chụp ảnh theo dõi",
      "description": "Chụp lại ảnh vùng bị thán thư sau 48h.",
      "due_at": "2026-07-06T08:00:00",
      "priority": "urgent",
      "type": "follow_up_photo"
    },
    {
      "title": "Kiểm tra bệnh",
      "description": "Kiểm tra ca thán thư có lan rộng thêm không.",
      "due_at": "2026-07-06T14:00:00",
      "priority": "urgent",
      "type": "disease_check"
    }
  ]
}
```

### Việc cụ thể team AI làm

```text
- Sinh lịch nhắc dựa trên độ tin cậy, mức độ bệnh, loại cây.
- Case nghi nấm: nhắc 48h.
- Case confidence thấp: nhắc chụp thêm góc khác.
- Case lan rộng: nhắc kiểm tra sớm hơn.
```

### Màn FE sử dụng

```text
Màn 4: Ca cần theo dõi
Màn 7: Lịch nhắc chăm sóc
```

---

## AI-07. Agent Trace / Nhật ký Agent

### Mục tiêu

Đây là màn rất quan trọng để chứng minh AI-native, multi-agent, không chỉ gọi model xong trả kết quả.

### Team AI phải trả log dạng này

```json
{
  "case_id": "CASE-2026-0704-001",
  "total_runtime_ms": 3800,
  "agents": [
    {
      "name": "Vision Agent",
      "input": "Ảnh lá/quả 1024x768",
      "output": "Phát hiện đốm nâu lõm ở tâm. Xác suất thán thư ban đầu 74%.",
      "features": {
        "lesion_count": 14,
        "leaf_area_affected": "18%",
        "image_quality": 0.91
      },
      "latency_ms": 820
    },
    {
      "name": "Symptom Agent",
      "input": "Top bệnh nghi ngờ",
      "output": "Hỏi thêm thời điểm xuất hiện, mưa kéo dài, vết bệnh lan sang quả chưa.",
      "features": {
        "rain_after": "3_days",
        "fruit_spots": true,
        "spread_speed": "medium"
      },
      "latency_ms": 510
    },
    {
      "name": "Context Agent",
      "input": "Vườn, thời tiết, nhật ký chăm sóc",
      "output": "Trảng Bom có mưa liên tục, độ ẩm 89%, chưa phun thuốc trong 7 ngày.",
      "latency_ms": 430
    },
    {
      "name": "Reasoning Agent",
      "input": "Vision + triệu chứng + bối cảnh",
      "output": "Tăng xác suất thán thư từ 74% lên 89%, loại trừ cháy lá do thuốc.",
      "latency_ms": 940
    }
  ]
}
```

### Màn FE sử dụng

```text
Màn 13: Nhật ký Agent
```

---

## AI-08. PyTorch Model Report

### Mục tiêu

Phục vụ PyTorch Award.

### Team AI phải chuẩn bị các chỉ số

```json
{
  "model_name": "EfficientNet-B0 fine-tuned",
  "framework": "PyTorch",
  "dataset": "PlantVillage + PlantDoc + ảnh seed demo",
  "top1_accuracy": 0.918,
  "macro_f1": 0.896,
  "latency_ms": 128,
  "model_size_mb": 21.4,
  "baseline": "ResNet18",
  "improvement": "+3.2%",
  "export": ["ONNX", "TorchScript"],
  "explainability": "Grad-CAM"
}
```

### Việc cụ thể team AI làm

```text
- Có notebook train/evaluate.
- Có file model.pth hoặc onnx.
- Có script inference.py.
- Có benchmark latency.
- Có confusion matrix.
- Có metric theo lớp bệnh.
- Có ảnh Grad-CAM minh họa.
```

### Màn FE sử dụng

```text
Màn 12: Model PyTorch
```

---

# 3. Team BE cần làm gì?

## BE-01. Thiết kế database

Team BE nên làm các bảng tối thiểu sau:

```text
users
farms
crops
diagnosis_cases
case_images
vision_results
symptom_questions
symptom_answers
diagnosis_results
treatment_plans
season_logs
reminders
disease_library
ipm_recommendations
expert_reviews
agent_logs
model_metrics
map_aggregates
```

## Bảng quan trọng nhất: diagnosis_cases

```sql
diagnosis_cases
- id
- case_code
- user_id
- farm_id
- crop_type
- growth_stage
- location_name
- status
- severity
- ai_confidence
- final_disease_code
- final_disease_name
- expert_required
- created_at
- updated_at
```

Status nên có:

```text
draft
image_uploaded
analyzed
waiting_symptoms
diagnosed
follow_up
need_expert
expert_confirmed
resolved
```

---

## BE-02. API cho Dashboard tổng quan

### Route FE

```text
/Tổng quan
```

### Endpoint

```http
GET /api/dashboard/overview
```

### Response

```json
{
  "alert": {
    "title": "Cảnh báo ổ dịch thán thư trên ớt tại Trảng Bom",
    "description": "12 ca được ghi nhận trong 7 ngày. AI khuyến nghị tỉa lá bệnh, giảm ẩm, chụp lại ảnh sau 48h.",
    "map_url": "/cooperative/disease-map"
  },
  "stats": {
    "open_cases": 7,
    "crop_types": 6,
    "today_reminders": 4,
    "model_accuracy": 91.8
  },
  "case_trend_7_days": [
    {
      "date": "2026-07-01",
      "new_cases": 3,
      "resolved_cases": 2,
      "expert_cases": 1
    }
  ],
  "crop_impact_ratio": [
    {
      "crop": "Ớt",
      "value": 35
    },
    {
      "crop": "Cà chua",
      "value": 20
    }
  ]
}
```

### BE cần làm

```text
- Tổng hợp số liệu từ diagnosis_cases, farms, reminders.
- Trả dữ liệu chart cho FE.
- Có dữ liệu seed đẹp để demo.
```

---

## BE-03. API quản lý vườn

### Route FE

```text
/quan-ly-vuon/vuon-cua-toi
```

### Endpoint

```http
GET /api/farms
POST /api/farms
GET /api/farms/{farm_id}
```

### Response

```json
{
  "farms": [
    {
      "id": "farm_001",
      "name": "Vườn ớt Trảng Bom",
      "location": "Trảng Bom, Đồng Nai",
      "area_m2": 2000,
      "crop_type": "Ớt",
      "growth_stage": "Ra hoa",
      "health_score": 62,
      "open_cases": 2,
      "last_check": "2026-07-04T08:30:00"
    }
  ]
}
```

### BE cần làm

```text
- CRUD vườn.
- Trả danh sách cây trồng.
- Trả sức khỏe vườn.
- Liên kết farm với diagnosis case.
```

---

## BE-04. API bắt đầu chẩn đoán mới

### Route FE

```text
/chan-doan/chan-doan-moi
```

### Endpoint bước 1

```http
POST /api/diagnosis/cases
```

### Request

```json
{
  "farm_id": "farm_001",
  "crop_type": "Ớt",
  "growth_stage": "Ra hoa",
  "location_name": "Trảng Bom, Đồng Nai"
}
```

### Response

```json
{
  "case_id": "case_001",
  "case_code": "CASE-2026-0704-001",
  "status": "draft",
  "next_step": "upload_image"
}
```

### BE cần làm

```text
- Tạo case mới.
- Gắn case với vườn.
- Trả case_id cho FE dùng xuyên suốt workflow.
```

---

## BE-05. API upload ảnh

### Endpoint

```http
POST /api/diagnosis/cases/{case_id}/images
```

### Request

```text
multipart/form-data
- image
- image_type: leaf | stem | fruit | whole_tree
```

### Response

```json
{
  "image_id": "img_001",
  "image_url": "/uploads/cases/case_001/leaf.jpg",
  "status": "uploaded",
  "next_step": "analyze_image"
}
```

### BE cần làm

```text
- Nhận file ảnh từ FE.
- Lưu local/S3/Cloudinary.
- Tạo record case_images.
- Không xử lý AI ở endpoint upload.
```

---

## BE-06. API gọi AI Vision

### Endpoint FE gọi

```http
POST /api/diagnosis/cases/{case_id}/analyze-image
```

### BE sẽ gọi nội bộ sang AI

```http
POST /ai/vision/analyze
```

### Response trả về FE

```json
{
  "case_id": "case_001",
  "status": "waiting_symptoms",
  "vision_result": {
    "image_quality": {
      "score": 0.91,
      "status": "good",
      "message": "Ảnh đạt yêu cầu, có thể phân tích."
    },
    "predictions": [
      {
        "disease_name": "Thán thư trên ớt",
        "confidence": 0.74
      },
      {
        "disease_name": "Đốm lá vi khuẩn",
        "confidence": 0.16
      },
      {
        "disease_name": "Cháy lá do thuốc",
        "confidence": 0.07
      }
    ],
    "heatmap_url": "/ai-results/CASE-001/gradcam.jpg"
  },
  "message": "AI chưa kết luận ngay. Cần hỏi thêm 3 câu để phân biệt nấm lá, thiếu dinh dưỡng và ngộ độc thuốc."
}
```

### BE cần làm

```text
- Lấy image_url, crop_type, farm context.
- Gọi AI Vision service.
- Lưu vision_results.
- Lưu agent_logs bước Vision Agent.
- Cập nhật diagnosis_cases.status = waiting_symptoms.
```

---

## BE-07. API lấy câu hỏi triệu chứng

### Endpoint

```http
GET /api/diagnosis/cases/{case_id}/symptom-questions
```

### Response

```json
{
  "case_id": "case_001",
  "questions": [
    {
      "id": "q1",
      "question": "Đốm bệnh xuất hiện sau mưa hay sau khi phun thuốc?",
      "type": "single_choice",
      "options": ["Sau mưa", "Sau phun thuốc", "Không rõ"]
    }
  ]
}
```

### BE cần làm

```text
- Gọi AI Symptom Agent hoặc lấy câu hỏi rule-based.
- Lưu symptom_questions.
- Trả câu hỏi cho FE chat.
```

---

## BE-08. API gửi câu trả lời triệu chứng

### Endpoint

```http
POST /api/diagnosis/cases/{case_id}/symptom-answers
```

### Request

```json
{
  "answers": [
    {
      "question_id": "q1",
      "answer": "Sau mưa"
    },
    {
      "question_id": "q2",
      "answer": "Lá già"
    },
    {
      "question_id": "q3",
      "answer": "Có, nhưng ít"
    }
  ]
}
```

### Response

```json
{
  "status": "symptoms_saved",
  "next_step": "final_diagnosis"
}
```

### BE cần làm

```text
- Lưu symptom_answers.
- Không kết luận tại endpoint này.
- Cho FE bấm “Xem kết luận” hoặc tự gọi finalize.
```

---

## BE-09. API kết luận chẩn đoán

### Endpoint

```http
POST /api/diagnosis/cases/{case_id}/finalize
```

### BE sẽ gọi các AI agent

```text
Context Agent
Reasoning Agent
Safety/IPM Agent
Follow-up Agent
```

### Response

```json
{
  "case_id": "case_001",
  "final_diagnosis": {
    "disease_name": "Thán thư trên ớt",
    "confidence": 0.89,
    "severity": "medium"
  },
  "differential_diagnosis": [
    "Đốm lá vi khuẩn",
    "Cháy lá do thuốc",
    "Thiếu kali"
  ],
  "reasoning": [
    "Ảnh có đốm nâu lan trên lá.",
    "Xuất hiện sau mưa.",
    "Bệnh bắt đầu từ lá già.",
    "Độ ẩm gần đây cao."
  ],
  "treatment_plan": {
    "immediate_actions": [
      "Tỉa lá bệnh nặng.",
      "Không tưới lên lá vào chiều tối.",
      "Tăng thông thoáng luống."
    ],
    "monitoring": [
      "Chụp lại sau 48 giờ.",
      "Kiểm tra mặt dưới lá."
    ],
    "safety_warning": "Ưu tiên IPM. Không khuyến nghị phun thuốc ngay nếu bệnh chưa lan rộng."
  },
  "created_reminders": [
    {
      "title": "Chụp ảnh theo dõi",
      "due_at": "2026-07-06T08:00:00"
    }
  ],
  "season_log_created": true,
  "expert_required": false
}
```

### BE cần làm cực kỳ quan trọng

```text
- Lưu diagnosis_results.
- Lưu treatment_plans.
- Tự tạo season_logs.
- Tự tạo reminders.
- Tự cập nhật diagnosis_cases.status.
- Nếu expert_required = true thì tạo expert_reviews.
- Ghi agent_logs đầy đủ.
```

Đây là endpoint quan trọng nhất của toàn demo.

---

# 4. API cho các màn danh sách

## Lịch sử chẩn đoán

### Route FE

```text
/chan-doan/lich-su-chan-doan
```

### Endpoint

```http
GET /api/diagnosis/history
```

### BE trả

```json
{
  "items": [
    {
      "case_id": "case_001",
      "crop_type": "Ớt",
      "farm_name": "Vườn ớt Trảng Bom",
      "disease_name": "Thán thư",
      "confidence": 0.89,
      "agents_count": 6,
      "status": "follow_up",
      "date": "2026-07-04"
    }
  ]
}
```

---

## Ca cần theo dõi

### Route FE

```text
/chan-doan/ca-can-theo-doi
```

### Endpoint

```http
GET /api/diagnosis/follow-up
PATCH /api/diagnosis/follow-up/{case_id}/resolve
```

### BE cần trả

```text
- Ca cần chụp lại ảnh
- Ca đang lan rộng
- Ca AI chưa chắc
- Ca chờ chuyên gia
```

---

## Nhật ký mùa vụ

### Route FE

```text
/quan-ly-vuon/nhat-ky-mua-vu
```

### Endpoint

```http
GET /api/season-logs
POST /api/season-logs
```

### BE cần làm

```text
- Tự tạo log sau mỗi chẩn đoán.
- Cho phép thêm log thủ công.
- Filter theo loại: bệnh, xử lý, kiểm tra, tưới, bón phân.
```

---

## Lịch nhắc chăm sóc

### Route FE

```text
/quan-ly-vuon/lich-nhac-cham-soc
```

### Endpoint

```http
GET /api/reminders
POST /api/reminders
PATCH /api/reminders/{id}/done
```

### BE cần làm

```text
- Lưu lịch nhắc do AI tạo.
- Cho phép đánh dấu đã làm.
- Trả nhóm hôm nay và 7 ngày tới.
```

---

## Thư viện bệnh cây

### Route FE

```text
/tri-thuc/thu-vien-benh-cay
```

### Endpoint

```http
GET /api/knowledge/diseases
GET /api/knowledge/diseases/{disease_code}
```

### BE cần làm

```text
- Seed sẵn 8–12 bệnh phổ biến.
- Có tên bệnh, tên khoa học, cây thường gặp, mức độ, nhóm bệnh.
- Dữ liệu này phục vụ cả FE và AI RAG/IPM.
```

---

## Khuyến nghị IPM

### Route FE

```text
/tri-thuc/khuyen-nghi-ipm
```

### Endpoint

```http
GET /api/knowledge/ipm
```

### BE cần làm

```text
- Trả 4 trụ cột IPM.
- Trả nguyên tắc 4 đúng.
- Trả khuyến nghị an toàn.
```

---

## Bản đồ ca bệnh

### Route FE

```text
/hop-tac-xa/ban-do-ca-benh
```

### Endpoint

```http
GET /api/cooperative/disease-map
```

### Response

```json
{
  "summary": {
    "total_cases": 35,
    "outbreak_zones": 5,
    "increased_this_week": 8,
    "decreasing_zones": 1
  },
  "regions": [
    {
      "name": "Trảng Bom",
      "lat": 10.966,
      "lng": 107.003,
      "case_count": 12,
      "risk_level": "high",
      "top_disease": "Thán thư trên ớt"
    }
  ],
  "recent_alerts": [
    {
      "disease": "Thán thư trên ớt",
      "location": "Trảng Bom",
      "case_count": 12,
      "date": "2026-07-04"
    }
  ]
}
```

### BE cần làm

```text
- Aggregate diagnosis_cases theo khu vực.
- Trả data cho bản đồ giả lập.
- Không cần bản đồ thật quá phức tạp, chỉ cần tọa độ/mô phỏng vùng Đồng Nai.
```

---

## Chuyên gia xác nhận

### Route FE

```text
/hop-tac-xa/chuyen-gia-xac-nhan
```

### Endpoint

```http
GET /api/expert/reviews
PATCH /api/expert/reviews/{review_id}/confirm
PATCH /api/expert/reviews/{review_id}/correct
POST /api/expert/reviews/{review_id}/note
```

### BE cần làm

```text
- Tạo review nếu AI confidence thấp hoặc bệnh nghiêm trọng.
- Cho chuyên gia xác nhận đúng.
- Cho chuyên gia sửa chẩn đoán.
- Ghi lại vào diagnosis_cases và agent_logs.
```

---

## Model PyTorch

### Route FE

```text
/he-thong-ai/model-pytorch
```

### Endpoint

```http
GET /api/ai/model-report
```

### BE cần làm

```text
- Không tính metric ở runtime.
- Chỉ đọc file JSON do team AI cung cấp.
- Trả về accuracy, F1, latency, model size, confusion matrix.
```

---

## Nhật ký Agent

### Route FE

```text
/he-thong-ai/nhat-ky-agent
```

### Endpoint

```http
GET /api/ai/agent-logs
GET /api/ai/agent-logs/{case_id}
```

### BE cần làm

```text
- Lưu từng bước agent chạy.
- Trả danh sách trace gần đây.
- Trả chi tiết từng case.
```

---

# 5. Chia nhiệm vụ theo người/nhóm

## Team AI

| Mã việc | Việc                              | Output bàn giao cho BE               |
| ------- | --------------------------------- | ------------------------------------ |
| AI-01   | Model phân loại bệnh bằng PyTorch | `/ai/vision/analyze`                 |
| AI-02   | Kiểm tra chất lượng ảnh           | `image_quality.score/status/message` |
| AI-03   | Grad-CAM / heatmap                | `heatmap_url`                        |
| AI-04   | Agent hỏi triệu chứng             | `/ai/symptom/questions`              |
| AI-05   | Agent tổng hợp bối cảnh           | `/ai/context/summarize`              |
| AI-06   | Agent suy luận chẩn đoán          | `/ai/reasoning/diagnose`             |
| AI-07   | Agent khuyến nghị IPM an toàn     | `/ai/safety/recommend`               |
| AI-08   | Agent tạo lịch nhắc               | `/ai/follow-up/reminders`            |
| AI-09   | Agent logs                        | JSON trace từng bước                 |
| AI-10   | Model report                      | `model_report.json`                  |

Team AI không cần làm database, không cần làm dashboard, không cần làm CRUD.

---

## Team BE

| Mã việc | Việc                    | Output bàn giao cho FE                        |
| ------- | ----------------------- | --------------------------------------------- |
| BE-01   | Database schema         | migrations + seed data                        |
| BE-02   | Auth/mock user          | user demo Admin/Farmer/Expert                 |
| BE-03   | API dashboard tổng quan | `/api/dashboard/overview`                     |
| BE-04   | API quản lý vườn        | `/api/farms`                                  |
| BE-05   | API tạo case chẩn đoán  | `/api/diagnosis/cases`                        |
| BE-06   | API upload ảnh          | `/api/diagnosis/cases/{id}/images`            |
| BE-07   | API gọi AI Vision       | `/api/diagnosis/cases/{id}/analyze-image`     |
| BE-08   | API triệu chứng         | `/api/diagnosis/cases/{id}/symptom-questions` |
| BE-09   | API kết luận cuối       | `/api/diagnosis/cases/{id}/finalize`          |
| BE-10   | API lịch sử chẩn đoán   | `/api/diagnosis/history`                      |
| BE-11   | API ca cần theo dõi     | `/api/diagnosis/follow-up`                    |
| BE-12   | API nhật ký mùa vụ      | `/api/season-logs`                            |
| BE-13   | API lịch nhắc           | `/api/reminders`                              |
| BE-14   | API thư viện bệnh/IPM   | `/api/knowledge/*`                            |
| BE-15   | API bản đồ HTX          | `/api/cooperative/disease-map`                |
| BE-16   | API chuyên gia xác nhận | `/api/expert/reviews`                         |
| BE-17   | API model report        | `/api/ai/model-report`                        |
| BE-18   | API agent logs          | `/api/ai/agent-logs`                          |

Team BE không cần train model, không cần tự viết reasoning AI, không cần làm lại giao diện.

---

# 6. Thứ tự ưu tiên làm để kịp demo

## Ưu tiên 1 — Bắt buộc phải có

```text
1. Tạo case chẩn đoán
2. Upload ảnh
3. AI Vision trả top bệnh
4. Chat hỏi triệu chứng
5. Final diagnosis
6. Treatment plan
7. Tự lưu nhật ký mùa vụ
8. Tự tạo lịch nhắc
9. Lịch sử chẩn đoán
10. Agent logs
```

Không có các mục này thì demo bị rời rạc.

---

## Ưu tiên 2 — Làm để thắng giải

```text
1. Dashboard tổng quan có số liệu động
2. Ca cần theo dõi
3. Bản đồ ca bệnh
4. Chuyên gia xác nhận
5. Model PyTorch Report
6. Grad-CAM
```

Những mục này tạo cảm giác sản phẩm có chiều sâu, có triển khai thật.

---

## Ưu tiên 3 — Làm nếu còn thời gian

```text
1. Auth phân quyền farmer/expert/admin
2. Realtime notification
3. Weather API thật
4. Bản đồ GIS thật
5. RAG tri thức nông nghiệp đầy đủ
6. Export báo cáo PDF
```

Không nên làm các mục này trước khi luồng demo chính chạy mượt.

---

# 7. Hợp đồng dữ liệu giữa AI và BE

Team AI nên đóng gói thành service riêng:

```text
ai-service/
├── app.py
├── models/
│   └── crop_disease_model.pth
├── services/
│   ├── vision_service.py
│   ├── symptom_agent.py
│   ├── context_agent.py
│   ├── reasoning_agent.py
│   ├── safety_agent.py
│   └── followup_agent.py
├── reports/
│   └── model_report.json
└── requirements.txt
```

BE gọi AI qua HTTP:

```text
POST /ai/vision/analyze
POST /ai/symptom/questions
POST /ai/context/summarize
POST /ai/reasoning/diagnose
POST /ai/safety/recommend
POST /ai/follow-up/reminders
GET  /ai/model-report
```

Trong trường hợp AI service lỗi, BE phải có fallback demo:

```text
Nếu AI timeout → dùng demo response cố định cho CASE-2026-0704-001.
```

Cái này rất quan trọng để tránh demo sân khấu bị chết.

---

# 8. Kịch bản phân công thực tế

## Bạn A — AI Vision/PyTorch

```text
- Train/fine-tune model.
- Làm inference API.
- Làm image quality check.
- Làm Grad-CAM.
- Xuất model report.
```

Deadline bàn giao:

```text
- API chạy được với 3–5 ảnh demo.
- Trả đúng JSON contract.
```

---

## Bạn B — AI Agent/Reasoning

```text
- Làm symptom questions.
- Làm context summary.
- Làm final reasoning.
- Làm IPM recommendation.
- Làm follow-up reminder suggestion.
- Làm agent trace output.
```

Deadline bàn giao:

```text
- Với case ớt/thán thư, cà chua/héo rũ, dưa leo/phấn trắng phải trả kết quả đẹp.
```

---

## Bạn C — BE Core Workflow

```text
- Database.
- Diagnosis case workflow.
- Upload image.
- Call AI service.
- Save diagnosis result.
- Save treatment plan.
- Save season log.
- Save reminders.
```

Đây là người quan trọng nhất của BE.

---

## Bạn D — BE Dashboard/Management

```text
- Dashboard overview.
- Farms.
- History.
- Follow-up cases.
- Season logs.
- Reminders.
- Disease library.
- IPM.
```

---

## Bạn E — BE Cooperative/Expert/AI System

```text
- Disease map.
- Expert review.
- Model report API.
- Agent logs API.
- Seed data cho dashboard.
```

---

# 9. Definition of Done cho demo thắng giải

Một case demo được xem là hoàn chỉnh khi chạy được chuỗi này:

```text
1. Vào Dashboard thấy cảnh báo ổ dịch.
2. Bấm Chẩn đoán mới.
3. Chọn cây Ớt + Vườn ớt Trảng Bom.
4. Upload ảnh bệnh.
5. AI trả Thán thư 74%, có heatmap.
6. AI hỏi thêm 3 câu.
7. User trả lời: sau mưa, lá già, có lan nhẹ.
8. AI kết luận Thán thư 89%.
9. AI giải thích vì sao kết luận.
10. AI khuyến nghị xử lý theo IPM.
11. Hệ thống tự lưu Nhật ký mùa vụ.
12. Hệ thống tự tạo lịch nhắc chụp lại sau 48h.
13. Case xuất hiện trong Lịch sử chẩn đoán.
14. Case xuất hiện trong Ca cần theo dõi.
15. Khu vực Trảng Bom tăng số ca trên Bản đồ ca bệnh.
16. Nhật ký Agent ghi Vision → Symptom → Context → Reasoning → Safety → Reminder.
17. Model PyTorch Report hiển thị accuracy, F1, latency, model size.
```

Nếu chạy mượt được 17 bước này, demo có cảm giác là một sản phẩm AI-native thật, không phải chỉ là app upload ảnh.

---

# 10. Chốt phân chia ngắn gọn

```text
Team AI:
Làm não của hệ thống.
- Vision model
- Symptom Agent
- Context Agent
- Reasoning Agent
- Safety/IPM Agent
- Follow-up Agent
- Agent trace
- PyTorch report

Team BE:
Làm xương sống sản phẩm.
- Database
- API
- Workflow chẩn đoán
- Upload ảnh
- Gọi AI
- Lưu kết quả
- Nhật ký mùa vụ
- Lịch nhắc
- Dashboard
- Bản đồ
- Chuyên gia xác nhận
- Agent logs

Team FE:
Không vẽ thêm màn.
- Gắn API vào UI có sẵn
- Bảo đảm luồng demo mượt
- Hiển thị loading/error/fallback đẹp
```

Chiến thuật đúng nhất: **AI làm kết quả đẹp và có giải thích, BE làm workflow chắc và lưu dữ liệu đầy đủ, FE chỉ cần nối giao diện hiện có thành một câu chuyện demo trọn vẹn.**
