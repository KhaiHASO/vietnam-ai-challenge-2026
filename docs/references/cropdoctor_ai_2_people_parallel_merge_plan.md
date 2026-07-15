# CropDoctor AI — Kế hoạch chia việc 2 người làm song song, ghép không phụ thuộc tuần tự

> Tài liệu này dùng kèm với file `cropdoctor_ai_run_first_step_by_step.md`.  
> Mục tiêu: **2 người AI làm song song**, không chờ nhau, cuối cùng ghép bằng **JSON contract cố định**.  
> Triết lý: **người nào cũng có thể chạy demo riêng**, khi ghép chỉ thay mock bằng service thật.

---

## 0. Chốt chiến thuật chia việc

Team AI có 2 người:

```text
Người 1 — AI Core Runner
Nhiệm vụ chính:
- Chạy FastAPI thật.
- Load model PyTorch/HuggingFace sẵn.
- Gọi DeepSeek.
- Trả kết quả /api/analyze thật.
- Tạo service vision, quality, reasoning, safety.

Người 2 — AI Integration, Mock, Evaluation, Demo Package
Nhiệm vụ chính:
- Đóng băng JSON schema để FE/BE cắm được.
- Làm mock API chạy độc lập, không cần model, không cần API key.
- Làm demo cases, agent logs, sample responses.
- Làm smoke test, Postman collection, script test hàng loạt ảnh.
- Làm model report/demo report để ăn điểm trình bày.
- Làm tài liệu merge + checklist kiểm thử.
```

Người 1 và Người 2 **không chờ nhau**.  
Người 2 cứ mock theo contract. Người 1 cứ làm service thật theo contract. Khi ghép, chỉ đổi:

```text
mock_analyze_result.json
→ real_analyze_result_from_services
```

---

## 1. Nguyên tắc vàng để làm song song

### 1.1. Không dùng “đợi người kia làm xong”

Sai:

```text
Đợi Người 1 chạy model xong rồi Người 2 mới làm FE/test/report.
```

Đúng:

```text
Người 2 tự tạo mock response giống hệt response thật.
FE/BE/test/report đều chạy bằng mock trước.
Khi Người 1 có API thật thì thay URL mock bằng URL thật.
```

### 1.2. Contract là luật

Hai người chỉ cần thống nhất 3 thứ:

```text
1. Endpoint
2. Request format
3. Response JSON format
```

Không cần biết bên trong người kia code thế nào.

### 1.3. Mọi output phải là JSON ổn định

Không để LLM trả văn xuôi tự do cho FE parse.  
Không thay key lung tung.  
Không đổi tên field sát giờ demo.

---

## 2. Cấu trúc repo chia ownership

Dùng chung repo:

```text
cropdoctor-ai-mvp/
├── api/
│   ├── main.py
│   ├── app/
│   │   ├── schemas.py                         # chung, không tự ý sửa sau khi freeze
│   │   ├── services/
│   │   │   ├── vision_service.py              # Người 1
│   │   │   ├── image_quality_service.py       # Người 1
│   │   │   ├── deepseek_service.py            # Người 1
│   │   │   ├── reasoning_service.py           # Người 1
│   │   │   ├── safety_service.py              # Người 1
│   │   │   └── logging_service.py             # Người 1 + Người 2 thống nhất format
│   │   ├── data/
│   │   │   ├── knowledge_base.json            # Người 2 seed trước, Người 1 dùng sau
│   │   │   ├── disease_actions.json           # Người 2
│   │   │   ├── demo_cases.json                # Người 2
│   │   │   └── mock_analyze_responses.json    # Người 2
│   │   └── storage/
│   │       ├── uploads/                       # runtime
│   │       └── agent_logs.jsonl               # runtime
│   ├── tests/
│   │   ├── test_schema_contract.py            # Người 2
│   │   ├── test_mock_api.py                   # Người 2
│   │   └── test_real_api_smoke.py             # Người 2
│   └── scripts/
│       ├── smoke_test.py                      # Người 2
│       ├── batch_test_images.py               # Người 2
│       └── generate_demo_report.py            # Người 2
├── mock_server/
│   ├── main.py                               # Người 2
│   ├── requirements.txt                      # Người 2
│   └── README.md                             # Người 2
├── contracts/
│   ├── analyze_request.schema.json           # Người 2 tạo, cả team dùng
│   ├── analyze_response.schema.json          # Người 2 tạo, cả team dùng
│   └── openapi_notes.md                      # Người 2
├── postman/
│   └── CropDoctor_AI.postman_collection.json # Người 2
├── demo_assets/
│   ├── images/                               # Người 2 gom ảnh demo
│   ├── sample_outputs/                       # Người 2
│   └── screenshots/                          # Người 2
├── docs/
│   ├── merge_guide.md                        # Người 2
│   ├── demo_script.md                        # Người 2
│   ├── model_card.md                         # Người 1 input, Người 2 đóng gói
│   ├── ai_architecture.md                    # Người 2
│   ├── pytorch_award_notes.md                # Người 2
│   └── testing_report.md                     # Người 2
└── README.md
```

---

## 3. Phân nhánh Git để không đụng nhau

### 3.1. Branch đề xuất

```bash
git checkout -b ai-core-runner
# dành cho Người 1

 git checkout -b ai-integration-demo-package
# dành cho Người 2
```

Khi ghép:

```bash
git checkout main
git pull

git merge ai-integration-demo-package
# merge contract, mock, tests, docs trước

git merge ai-core-runner
# merge service thật sau
```

### 3.2. File không được sửa lung tung

Sau khi freeze, 2 người không tự ý đổi các file này:

```text
api/app/schemas.py
contracts/analyze_request.schema.json
contracts/analyze_response.schema.json
```

Muốn đổi phải báo cả team vì FE/BE sẽ phụ thuộc vào schema.

---

## 4. Contract chung bắt buộc dùng

### 4.1. Endpoint chính

```http
POST /api/analyze
Content-Type: multipart/form-data
```

Input:

```text
image: file ảnh lá cây
crop_type: string, optional
location: string, optional
notes: string, optional
use_mock: boolean, optional
```

Ví dụ curl:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "image=@demo_assets/images/chili_anthracnose.jpg" \
  -F "crop_type=Ớt" \
  -F "location=Đồng Nai" \
  -F "notes=Lá/quả xuất hiện đốm sau mưa"
```

### 4.2. Response JSON chuẩn

Đây là response mà cả Người 1 và Người 2 phải tuân thủ:

```json
{
  "request_id": "req_20260704_0001",
  "status": "success",
  "demo_mode": true,
  "input": {
    "filename": "chili_anthracnose.jpg",
    "crop_type": "Ớt",
    "location": "Đồng Nai",
    "notes": "Lá/quả xuất hiện đốm sau mưa"
  },
  "image_quality": {
    "score": 0.91,
    "status": "good",
    "issues": [],
    "message": "Ảnh đạt yêu cầu để phân tích."
  },
  "vision": {
    "model_name": "mesabo/agri-plant-disease-resnet50",
    "framework": "PyTorch",
    "top_predictions": [
      {
        "label": "Pepper bell Bacterial spot",
        "label_vi": "Đốm vi khuẩn trên ớt",
        "confidence": 0.78
      },
      {
        "label": "Tomato Bacterial spot",
        "label_vi": "Đốm vi khuẩn trên cà chua",
        "confidence": 0.12
      },
      {
        "label": "Pepper bell healthy",
        "label_vi": "Ớt khỏe mạnh",
        "confidence": 0.05
      }
    ],
    "gradcam_url": null
  },
  "reasoning": {
    "final_diagnosis": "Nghi ngờ bệnh đốm vi khuẩn trên ớt",
    "confidence": 0.74,
    "severity": "medium",
    "evidence": [
      "Model thị giác xếp bệnh đốm vi khuẩn cao nhất.",
      "Ghi chú người dùng có nhắc xuất hiện đốm sau mưa.",
      "Cây ớt thường nhạy với bệnh đốm lá khi ẩm độ cao."
    ],
    "uncertainties": [
      "Chưa có ảnh mặt dưới lá.",
      "Chưa biết bệnh có lan sang quả hay thân không."
    ]
  },
  "recommendation": {
    "ipm_steps": [
      "Cách ly hoặc đánh dấu khu vực cây bị nặng để theo dõi.",
      "Tỉa bỏ lá bị bệnh nặng, không vứt lá bệnh ngay trong luống.",
      "Hạn chế tưới phun lên lá vào chiều tối.",
      "Theo dõi 2-3 ngày, nếu bệnh lan nhanh nên hỏi cán bộ kỹ thuật địa phương."
    ],
    "chemical_warning": "Không tự ý phối thuốc hoặc tăng liều. Nếu dùng thuốc BVTV, phải theo nhãn, đúng cây trồng, đúng bệnh, đúng liều, đúng thời gian cách ly.",
    "expert_required": false
  },
  "follow_up_questions": [
    "Vết bệnh nằm chủ yếu trên lá già hay lá non?",
    "Mặt dưới lá có đốm ướt nước hoặc quầng vàng không?",
    "Bệnh có xuất hiện sau mưa hoặc sau khi tưới phun không?"
  ],
  "agent_logs": [
    {
      "agent": "ImageQualityAgent",
      "status": "done",
      "summary": "Ảnh đủ sáng, không quá mờ.",
      "duration_ms": 41
    },
    {
      "agent": "VisionAgent",
      "status": "done",
      "summary": "Top-1 là Pepper bell Bacterial spot với confidence 0.78.",
      "duration_ms": 412
    },
    {
      "agent": "ReasoningAgent",
      "status": "done",
      "summary": "Kết hợp prediction, crop type và notes để đưa ra chẩn đoán nghi ngờ.",
      "duration_ms": 982
    },
    {
      "agent": "SafetyIPMAgent",
      "status": "done",
      "summary": "Ưu tiên IPM, không kê thuốc cụ thể.",
      "duration_ms": 120
    }
  ],
  "created_at": "2026-07-04T21:30:00+07:00"
}
```

---

## 5. Việc của Người 1 — AI Core Runner

Người 1 cứ theo file kế hoạch cũ. Tóm tắt lại phần cần làm:

### 5.1. Mục tiêu của Người 1

```text
Mục tiêu cuối:
POST /api/analyze chạy thật bằng FastAPI.
Có load model PyTorch/HuggingFace.
Có gọi DeepSeek nếu có API key.
Có fallback nếu model hoặc LLM lỗi.
Response khớp schema chung.
```

### 5.2. Checklist Người 1

```text
[ ] Tạo FastAPI project.
[ ] Cài torch, torchvision, transformers, fastapi.
[ ] Load model mesabo/agri-plant-disease-resnet50.
[ ] Viết vision_service.py trả top-3 prediction.
[ ] Viết image_quality_service.py check blur/brightness đơn giản.
[ ] Viết deepseek_service.py gọi DeepSeek theo OpenAI-compatible client.
[ ] Viết reasoning_service.py nhận vision result + notes → final diagnosis.
[ ] Viết safety_service.py lọc khuyến nghị an toàn.
[ ] Viết logging_service.py append JSONL.
[ ] Endpoint /api/analyze trả response theo contract.
[ ] Chạy smoke test bằng ảnh bất kỳ.
[ ] Nếu model lỗi, bật DEMO_MODE=true để trả mock nhưng API vẫn sống.
```

### 5.3. File Người 1 được ưu tiên sửa

```text
api/main.py
api/app/config.py
api/app/services/vision_service.py
api/app/services/image_quality_service.py
api/app/services/deepseek_service.py
api/app/services/reasoning_service.py
api/app/services/safety_service.py
api/app/services/logging_service.py
```

### 5.4. Output bàn giao cho Người 2

Người 1 không cần viết report dài. Chỉ cần bàn giao:

```text
1. API chạy ở http://localhost:8000
2. Swagger chạy ở http://localhost:8000/docs
3. Một file sample response thật: demo_assets/sample_outputs/real_response_001.json
4. Ảnh chụp màn hình Swagger hoặc terminal chạy thành công
5. Nếu có metric model thì đưa vào docs/model_card.md
```

---

## 6. Việc của Người 2 — AI Integration, Mock, Evaluation, Demo Package

Người 2 là người làm cho dự án **dù model chưa xong vẫn demo được**.

### 6.1. Mục tiêu của Người 2

```text
Mục tiêu cuối:
- Có mock API giống thật 100% schema.
- Có bộ demo case đẹp.
- Có test tự động để kiểm tra API thật/mock.
- Có Postman collection cho team test.
- Có docs/report/screenshot để trình bày.
- Có checklist merge giúp ghép vào không vỡ.
```

Người 2 **không cần API key DeepSeek**, **không cần GPU**, **không cần model chạy thật**.

---

# PHẦN A — Người 2 tạo contract schema

## A1. Tạo thư mục

Từ root repo:

```bash
mkdir -p contracts api/app/data api/tests api/scripts mock_server postman demo_assets/images demo_assets/sample_outputs docs
```

Windows PowerShell:

```powershell
mkdir contracts, api\app\data, api\tests, api\scripts, mock_server, postman, demo_assets\images, demo_assets\sample_outputs, docs
```

## A2. Tạo `contracts/analyze_response.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CropDoctor Analyze Response",
  "type": "object",
  "required": [
    "request_id",
    "status",
    "demo_mode",
    "input",
    "image_quality",
    "vision",
    "reasoning",
    "recommendation",
    "follow_up_questions",
    "agent_logs",
    "created_at"
  ],
  "properties": {
    "request_id": { "type": "string" },
    "status": { "type": "string", "enum": ["success", "warning", "error"] },
    "demo_mode": { "type": "boolean" },
    "input": {
      "type": "object",
      "required": ["filename", "crop_type", "location", "notes"],
      "properties": {
        "filename": { "type": "string" },
        "crop_type": { "type": ["string", "null"] },
        "location": { "type": ["string", "null"] },
        "notes": { "type": ["string", "null"] }
      }
    },
    "image_quality": {
      "type": "object",
      "required": ["score", "status", "issues", "message"],
      "properties": {
        "score": { "type": "number", "minimum": 0, "maximum": 1 },
        "status": { "type": "string", "enum": ["good", "acceptable", "poor"] },
        "issues": { "type": "array", "items": { "type": "string" } },
        "message": { "type": "string" }
      }
    },
    "vision": {
      "type": "object",
      "required": ["model_name", "framework", "top_predictions", "gradcam_url"],
      "properties": {
        "model_name": { "type": "string" },
        "framework": { "type": "string" },
        "top_predictions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["label", "label_vi", "confidence"],
            "properties": {
              "label": { "type": "string" },
              "label_vi": { "type": "string" },
              "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        },
        "gradcam_url": { "type": ["string", "null"] }
      }
    },
    "reasoning": {
      "type": "object",
      "required": ["final_diagnosis", "confidence", "severity", "evidence", "uncertainties"],
      "properties": {
        "final_diagnosis": { "type": "string" },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "severity": { "type": "string", "enum": ["low", "medium", "high", "unknown"] },
        "evidence": { "type": "array", "items": { "type": "string" } },
        "uncertainties": { "type": "array", "items": { "type": "string" } }
      }
    },
    "recommendation": {
      "type": "object",
      "required": ["ipm_steps", "chemical_warning", "expert_required"],
      "properties": {
        "ipm_steps": { "type": "array", "items": { "type": "string" } },
        "chemical_warning": { "type": "string" },
        "expert_required": { "type": "boolean" }
      }
    },
    "follow_up_questions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "agent_logs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["agent", "status", "summary", "duration_ms"],
        "properties": {
          "agent": { "type": "string" },
          "status": { "type": "string", "enum": ["done", "skipped", "failed"] },
          "summary": { "type": "string" },
          "duration_ms": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "created_at": { "type": "string" }
  }
}
```

## A3. Tạo `contracts/analyze_request.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CropDoctor Analyze Request",
  "type": "object",
  "required": ["image"],
  "properties": {
    "image": {
      "description": "Image file uploaded as multipart/form-data",
      "type": "string",
      "format": "binary"
    },
    "crop_type": {
      "type": ["string", "null"],
      "examples": ["Ớt", "Cà chua", "Lúa", "Dưa leo"]
    },
    "location": {
      "type": ["string", "null"],
      "examples": ["Đồng Nai", "Lâm Đồng", "Bình Dương"]
    },
    "notes": {
      "type": ["string", "null"]
    },
    "use_mock": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

# PHẦN B — Người 2 tạo mock data

## B1. Tạo `api/app/data/mock_analyze_responses.json`

```json
[
  {
    "case_id": "chili_bacterial_spot_001",
    "response": {
      "request_id": "mock_chili_001",
      "status": "success",
      "demo_mode": true,
      "input": {
        "filename": "chili_bacterial_spot.jpg",
        "crop_type": "Ớt",
        "location": "Đồng Nai",
        "notes": "Lá xuất hiện đốm sau mưa, lan nhẹ."
      },
      "image_quality": {
        "score": 0.91,
        "status": "good",
        "issues": [],
        "message": "Ảnh đạt yêu cầu để phân tích."
      },
      "vision": {
        "model_name": "mesabo/agri-plant-disease-resnet50",
        "framework": "PyTorch",
        "top_predictions": [
          {
            "label": "Pepper bell Bacterial spot",
            "label_vi": "Đốm vi khuẩn trên ớt",
            "confidence": 0.78
          },
          {
            "label": "Tomato Bacterial spot",
            "label_vi": "Đốm vi khuẩn trên cà chua",
            "confidence": 0.12
          },
          {
            "label": "Pepper bell healthy",
            "label_vi": "Ớt khỏe mạnh",
            "confidence": 0.05
          }
        ],
        "gradcam_url": null
      },
      "reasoning": {
        "final_diagnosis": "Nghi ngờ bệnh đốm vi khuẩn trên ớt",
        "confidence": 0.74,
        "severity": "medium",
        "evidence": [
          "Model thị giác xếp bệnh đốm vi khuẩn cao nhất.",
          "Ghi chú người dùng cho biết bệnh xuất hiện sau mưa.",
          "Triệu chứng đốm lá phù hợp với nhóm bệnh đốm trên cây ớt."
        ],
        "uncertainties": [
          "Chưa có ảnh mặt dưới lá.",
          "Chưa biết bệnh có lan sang quả hay thân không."
        ]
      },
      "recommendation": {
        "ipm_steps": [
          "Đánh dấu cây bị bệnh để theo dõi riêng.",
          "Tỉa bỏ lá bệnh nặng, thu gom khỏi khu vực trồng.",
          "Hạn chế tưới phun lên lá vào chiều tối.",
          "Theo dõi 2-3 ngày, nếu bệnh lan nhanh nên hỏi cán bộ kỹ thuật địa phương."
        ],
        "chemical_warning": "Không tự ý phối thuốc hoặc tăng liều. Nếu dùng thuốc BVTV, phải theo nhãn, đúng cây trồng, đúng bệnh, đúng liều, đúng thời gian cách ly.",
        "expert_required": false
      },
      "follow_up_questions": [
        "Vết bệnh nằm chủ yếu trên lá già hay lá non?",
        "Mặt dưới lá có đốm ướt nước hoặc quầng vàng không?",
        "Bệnh có xuất hiện sau mưa hoặc sau khi tưới phun không?"
      ],
      "agent_logs": [
        {
          "agent": "ImageQualityAgent",
          "status": "done",
          "summary": "Ảnh đủ sáng, không quá mờ.",
          "duration_ms": 41
        },
        {
          "agent": "VisionAgent",
          "status": "done",
          "summary": "Top-1 là Pepper bell Bacterial spot với confidence 0.78.",
          "duration_ms": 412
        },
        {
          "agent": "ReasoningAgent",
          "status": "done",
          "summary": "Kết hợp prediction, crop type và notes để đưa ra chẩn đoán nghi ngờ.",
          "duration_ms": 982
        },
        {
          "agent": "SafetyIPMAgent",
          "status": "done",
          "summary": "Ưu tiên IPM, không kê thuốc cụ thể.",
          "duration_ms": 120
        }
      ],
      "created_at": "2026-07-04T21:30:00+07:00"
    }
  },
  {
    "case_id": "tomato_late_blight_001",
    "response": {
      "request_id": "mock_tomato_001",
      "status": "success",
      "demo_mode": true,
      "input": {
        "filename": "tomato_late_blight.jpg",
        "crop_type": "Cà chua",
        "location": "Lâm Đồng",
        "notes": "Lá có mảng nâu lớn, trời ẩm, vài cây lan nhanh."
      },
      "image_quality": {
        "score": 0.88,
        "status": "good",
        "issues": [],
        "message": "Ảnh rõ, đủ sáng, có thể phân tích."
      },
      "vision": {
        "model_name": "mesabo/agri-plant-disease-resnet50",
        "framework": "PyTorch",
        "top_predictions": [
          {
            "label": "Tomato Late blight",
            "label_vi": "Bệnh mốc sương cà chua",
            "confidence": 0.83
          },
          {
            "label": "Tomato Early blight",
            "label_vi": "Bệnh cháy lá sớm cà chua",
            "confidence": 0.09
          },
          {
            "label": "Tomato healthy",
            "label_vi": "Cà chua khỏe mạnh",
            "confidence": 0.03
          }
        ],
        "gradcam_url": null
      },
      "reasoning": {
        "final_diagnosis": "Nghi ngờ bệnh mốc sương trên cà chua",
        "confidence": 0.81,
        "severity": "high",
        "evidence": [
          "Top-1 prediction là Tomato Late blight.",
          "Người dùng mô tả bệnh lan nhanh trong điều kiện ẩm.",
          "Mảng nâu lớn trên lá là dấu hiệu cần xử lý sớm."
        ],
        "uncertainties": [
          "Chưa biết mặt dưới lá có lớp mốc trắng hay không.",
          "Chưa có thông tin về tình trạng trên thân và quả."
        ]
      },
      "recommendation": {
        "ipm_steps": [
          "Kiểm tra ngay các cây xung quanh vì mức độ lan có thể nhanh.",
          "Tỉa bỏ lá bệnh nặng, tránh làm rơi vụn lá bệnh trong luống.",
          "Giảm ẩm tán lá, tăng thông thoáng nếu trồng nhà màng.",
          "Nếu bệnh lan nhanh, nên liên hệ kỹ thuật viên/cán bộ BVTV địa phương."
        ],
        "chemical_warning": "Không đưa tên thuốc cụ thể khi chưa đối chiếu danh mục được phép và nhãn thuốc tại địa phương. Luôn tuân thủ bảo hộ, liều lượng và thời gian cách ly.",
        "expert_required": true
      },
      "follow_up_questions": [
        "Mặt dưới lá có lớp mốc trắng/xám vào sáng sớm không?",
        "Bệnh đã lan sang thân hoặc quả chưa?",
        "Ruộng/vườn có bị ẩm kéo dài sau mưa không?"
      ],
      "agent_logs": [
        {
          "agent": "ImageQualityAgent",
          "status": "done",
          "summary": "Ảnh đạt chất lượng phân tích.",
          "duration_ms": 38
        },
        {
          "agent": "VisionAgent",
          "status": "done",
          "summary": "Top-1 là Tomato Late blight với confidence 0.83.",
          "duration_ms": 436
        },
        {
          "agent": "ReasoningAgent",
          "status": "done",
          "summary": "Mức độ nghiêm trọng cao do bệnh có dấu hiệu lan nhanh.",
          "duration_ms": 1010
        },
        {
          "agent": "SafetyIPMAgent",
          "status": "done",
          "summary": "Bật expert_required do severity high.",
          "duration_ms": 145
        }
      ],
      "created_at": "2026-07-04T21:31:00+07:00"
    }
  }
]
```

## B2. Tạo `api/app/data/disease_actions.json`

```json
{
  "default": {
    "ipm_steps": [
      "Chụp thêm ảnh rõ mặt trên và mặt dưới lá.",
      "Theo dõi tốc độ lan trong 2-3 ngày.",
      "Tỉa bỏ bộ phận bệnh nặng nếu cần.",
      "Giữ vườn thông thoáng và tránh tưới phun lên lá vào chiều tối."
    ],
    "chemical_warning": "Không tự ý dùng thuốc khi chưa xác định rõ bệnh và chưa đọc nhãn thuốc. Ưu tiên hỏi cán bộ kỹ thuật địa phương nếu bệnh lan nhanh."
  },
  "Tomato Late blight": {
    "ipm_steps": [
      "Tăng thông thoáng tán lá và giảm ẩm kéo dài.",
      "Loại bỏ lá bệnh nặng khỏi vườn.",
      "Theo dõi cây lân cận vì bệnh có thể lan nhanh trong điều kiện ẩm.",
      "Liên hệ kỹ thuật viên nếu xuất hiện trên diện rộng."
    ],
    "expert_required": true
  },
  "Pepper bell Bacterial spot": {
    "ipm_steps": [
      "Tránh tưới phun trực tiếp lên lá.",
      "Tỉa bỏ lá bị bệnh nặng.",
      "Vệ sinh dụng cụ sau khi xử lý cây bệnh.",
      "Theo dõi vết bệnh sau mưa hoặc sau tưới."
    ],
    "expert_required": false
  }
}
```

## B3. Tạo `api/app/data/demo_cases.json`

```json
[
  {
    "case_id": "case_01_chili",
    "title": "Ớt bị đốm lá sau mưa",
    "image_name": "chili_bacterial_spot.jpg",
    "crop_type": "Ớt",
    "location": "Đồng Nai",
    "notes": "Lá xuất hiện đốm sau mưa, lan nhẹ.",
    "expected_top1": "Pepper bell Bacterial spot",
    "expected_severity": "medium",
    "demo_message": "Case an toàn để demo vì kết quả dễ hiểu, không quá nghiêm trọng."
  },
  {
    "case_id": "case_02_tomato",
    "title": "Cà chua nghi mốc sương",
    "image_name": "tomato_late_blight.jpg",
    "crop_type": "Cà chua",
    "location": "Lâm Đồng",
    "notes": "Lá có mảng nâu lớn, trời ẩm, vài cây lan nhanh.",
    "expected_top1": "Tomato Late blight",
    "expected_severity": "high",
    "demo_message": "Case dùng để show agent bật cảnh báo cần chuyên gia."
  },
  {
    "case_id": "case_03_unknown",
    "title": "Ảnh mờ cần chụp lại",
    "image_name": "blur_leaf.jpg",
    "crop_type": "Không rõ",
    "location": "Không rõ",
    "notes": "Ảnh chụp tối và mờ.",
    "expected_top1": "unknown",
    "expected_severity": "unknown",
    "demo_message": "Case dùng để show hệ thống không phán bừa khi ảnh kém."
  }
]
```

---

# PHẦN C — Người 2 tạo mock API chạy độc lập

Mock API giúp FE/BE test ngay cả khi Người 1 chưa chạy xong model.

## C1. Tạo `mock_server/requirements.txt`

```txt
fastapi==0.116.1
uvicorn[standard]==0.35.0
python-multipart==0.0.20
```

## C2. Tạo `mock_server/main.py`

```python
from __future__ import annotations

import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
MOCK_FILE = ROOT / "api" / "app" / "data" / "mock_analyze_responses.json"

app = FastAPI(title="CropDoctor AI Mock API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def now_vn_iso() -> str:
    tz = timezone(timedelta(hours=7))
    return datetime.now(tz).isoformat(timespec="seconds")


def load_mock_responses() -> list[dict]:
    if not MOCK_FILE.exists():
        raise FileNotFoundError(f"Missing mock file: {MOCK_FILE}")
    return json.loads(MOCK_FILE.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "cropdoctor-ai-mock",
        "mode": "mock",
        "time": now_vn_iso(),
    }


@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    crop_type: Optional[str] = Form(default=None),
    location: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    use_mock: bool = Form(default=True),
) -> dict:
    records = load_mock_responses()

    selected = None
    crop_lower = (crop_type or "").lower()
    filename_lower = (image.filename or "").lower()

    for item in records:
        resp = item["response"]
        resp_crop = (resp["input"].get("crop_type") or "").lower()
        resp_file = (resp["input"].get("filename") or "").lower()
        if resp_crop and resp_crop in crop_lower:
            selected = resp
            break
        if resp_file and resp_file in filename_lower:
            selected = resp
            break

    if selected is None:
        selected = random.choice(records)["response"]

    result = json.loads(json.dumps(selected, ensure_ascii=False))
    result["request_id"] = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    result["demo_mode"] = True
    result["created_at"] = now_vn_iso()
    result["input"]["filename"] = image.filename or result["input"]["filename"]
    result["input"]["crop_type"] = crop_type or result["input"].get("crop_type")
    result["input"]["location"] = location or result["input"].get("location")
    result["input"]["notes"] = notes or result["input"].get("notes")

    return result
```

## C3. Chạy mock API

```bash
cd cropdoctor-ai-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r mock_server/requirements.txt
uvicorn mock_server.main:app --host 0.0.0.0 --port 8001 --reload
```

Windows PowerShell:

```powershell
cd cropdoctor-ai-mvp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r mock_server\requirements.txt
uvicorn mock_server.main:app --host 0.0.0.0 --port 8001 --reload
```

Test:

```bash
curl http://localhost:8001/health
```

Upload test bằng ảnh bất kỳ:

```bash
curl -X POST "http://localhost:8001/api/analyze" \
  -F "image=@demo_assets/images/test.jpg" \
  -F "crop_type=Ớt" \
  -F "location=Đồng Nai" \
  -F "notes=Lá xuất hiện đốm sau mưa"
```

Khi Người 1 chưa xong:

```text
FE gọi http://localhost:8001/api/analyze
```

Khi Người 1 xong:

```text
FE đổi sang http://localhost:8000/api/analyze
```

---

# PHẦN D — Người 2 tạo script test schema

## D1. Cài package test

Thêm vào `api/requirements.txt` hoặc cài riêng:

```bash
pip install jsonschema requests pytest
```

## D2. Tạo `api/tests/test_schema_contract.py`

```python
import json
from pathlib import Path

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts" / "analyze_response.schema.json"
MOCK_PATH = ROOT / "api" / "app" / "data" / "mock_analyze_responses.json"


def test_all_mock_responses_match_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    records = json.loads(MOCK_PATH.read_text(encoding="utf-8"))

    assert records, "mock_analyze_responses.json is empty"

    for item in records:
        validate(instance=item["response"], schema=schema)
```

Chạy:

```bash
pytest api/tests/test_schema_contract.py -q
```

Kết quả mong muốn:

```text
1 passed
```

## D3. Tạo `api/scripts/smoke_test.py`

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8001/api/analyze")
    parser.add_argument("--image", required=True)
    parser.add_argument("--crop-type", default="Ớt")
    parser.add_argument("--location", default="Đồng Nai")
    parser.add_argument("--notes", default="Lá xuất hiện đốm sau mưa")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    with image_path.open("rb") as f:
        files = {"image": (image_path.name, f, "image/jpeg")}
        data = {
            "crop_type": args.crop_type,
            "location": args.location,
            "notes": args.notes,
        }
        res = requests.post(args.url, files=files, data=data, timeout=60)

    print("STATUS:", res.status_code)
    print(json.dumps(res.json(), ensure_ascii=False, indent=2))
    res.raise_for_status()


if __name__ == "__main__":
    main()
```

Chạy với mock:

```bash
python api/scripts/smoke_test.py \
  --url http://localhost:8001/api/analyze \
  --image demo_assets/images/test.jpg \
  --crop-type "Ớt"
```

Chạy với API thật của Người 1:

```bash
python api/scripts/smoke_test.py \
  --url http://localhost:8000/api/analyze \
  --image demo_assets/images/test.jpg \
  --crop-type "Ớt"
```

---

# PHẦN E — Người 2 tạo batch test để sinh report

## E1. Tạo `api/scripts/batch_test_images.py`

```python
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8001/api/analyze")
    parser.add_argument("--image-dir", default="demo_assets/images")
    parser.add_argument("--out", default="demo_assets/sample_outputs/batch_results.csv")
    args = parser.parse_args()

    image_dir = Path(args.image_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    image_paths = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpeg"))
    if not image_paths:
        raise RuntimeError(f"No images found in {image_dir}")

    rows = []
    for image_path in image_paths:
        started = time.perf_counter()
        with image_path.open("rb") as f:
            files = {"image": (image_path.name, f, "image/jpeg")}
            data = {"crop_type": "", "location": "", "notes": "batch test"}
            res = requests.post(args.url, files=files, data=data, timeout=60)
        latency_ms = round((time.perf_counter() - started) * 1000)

        try:
            payload = res.json()
            top1 = payload["vision"]["top_predictions"][0]
            rows.append({
                "image": image_path.name,
                "status_code": res.status_code,
                "latency_ms": latency_ms,
                "final_diagnosis": payload["reasoning"]["final_diagnosis"],
                "severity": payload["reasoning"]["severity"],
                "top1_label": top1["label"],
                "top1_label_vi": top1["label_vi"],
                "top1_confidence": top1["confidence"],
                "expert_required": payload["recommendation"]["expert_required"],
            })
        except Exception as exc:
            rows.append({
                "image": image_path.name,
                "status_code": res.status_code,
                "latency_ms": latency_ms,
                "final_diagnosis": f"ERROR: {exc}",
                "severity": "error",
                "top1_label": "",
                "top1_label_vi": "",
                "top1_confidence": "",
                "expert_required": "",
            })

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python api/scripts/batch_test_images.py \
  --url http://localhost:8001/api/analyze \
  --image-dir demo_assets/images \
  --out demo_assets/sample_outputs/batch_results.csv
```

Khi API thật xong:

```bash
python api/scripts/batch_test_images.py \
  --url http://localhost:8000/api/analyze \
  --image-dir demo_assets/images \
  --out demo_assets/sample_outputs/batch_results_real_api.csv
```

---

# PHẦN F — Người 2 tạo tài liệu demo/report

## F1. Tạo `docs/demo_script.md`

```md
# Demo Script — CropDoctor AI

## Mục tiêu demo

Chứng minh hệ thống có thể:

1. Nhận ảnh cây trồng.
2. Kiểm tra chất lượng ảnh.
3. Dự đoán bệnh bằng PyTorch model.
4. Kết hợp ngữ cảnh người dùng.
5. Sinh chẩn đoán có giải thích.
6. Đưa khuyến nghị IPM an toàn.
7. Ghi lại nhật ký từng agent.

## Luồng demo 1 — Case ớt đốm lá

Input:

- Crop: Ớt
- Location: Đồng Nai
- Notes: Lá xuất hiện đốm sau mưa, lan nhẹ.

Điểm cần nói:

- VisionAgent nhận diện top-1 là đốm vi khuẩn trên ớt.
- ReasoningAgent không chỉ lấy model prediction mà còn dùng ghi chú sau mưa.
- SafetyIPMAgent không kê thuốc bừa, ưu tiên IPM.
- FollowUpAgent hỏi thêm mặt dưới lá, lá già/lá non, điều kiện sau mưa.

## Luồng demo 2 — Case cà chua mốc sương

Input:

- Crop: Cà chua
- Location: Lâm Đồng
- Notes: Lá có mảng nâu lớn, trời ẩm, vài cây lan nhanh.

Điểm cần nói:

- Severity high.
- expert_required = true.
- Hệ thống biết nâng cấp cảnh báo khi bệnh có nguy cơ lan nhanh.

## Luồng demo 3 — Ảnh mờ

Input:

- Ảnh thiếu sáng/mờ.

Điểm cần nói:

- ImageQualityAgent phát hiện ảnh kém.
- Hệ thống yêu cầu chụp lại thay vì phán bừa.
```

## F2. Tạo `docs/ai_architecture.md`

```md
# AI Architecture — CropDoctor AI

## Tổng quan

CropDoctor AI dùng kiến trúc nhiều agent nhưng triển khai theo hướng thực dụng:

```text
Image Upload
→ ImageQualityAgent
→ VisionAgent
→ ReasoningAgent
→ SafetyIPMAgent
→ FollowUpAgent
→ LoggingAgent
→ JSON Response
```

## Agent 1 — ImageQualityAgent

Nhiệm vụ:

- Kiểm tra ảnh mờ.
- Kiểm tra ảnh quá tối/quá sáng.
- Kiểm tra ảnh có đủ điều kiện phân tích không.

Output:

```json
{
  "score": 0.91,
  "status": "good",
  "issues": [],
  "message": "Ảnh đạt yêu cầu để phân tích."
}
```

## Agent 2 — VisionAgent

Nhiệm vụ:

- Chạy PyTorch/HuggingFace model.
- Trả top-3 bệnh.
- Sau này có thể bổ sung Grad-CAM.

Output:

```json
{
  "model_name": "mesabo/agri-plant-disease-resnet50",
  "framework": "PyTorch",
  "top_predictions": []
}
```

## Agent 3 — ReasoningAgent

Nhiệm vụ:

- Kết hợp kết quả vision với crop type, location, notes.
- Sinh final diagnosis.
- Ghi rõ evidence và uncertainty.

## Agent 4 — SafetyIPMAgent

Nhiệm vụ:

- Không kê thuốc bừa.
- Ưu tiên IPM.
- Bật expert_required nếu severity cao hoặc confidence thấp.

## Agent 5 — FollowUpAgent

Nhiệm vụ:

- Sinh câu hỏi tiếp theo để xác nhận bệnh.
- Hỗ trợ người dùng bổ sung thông tin.

## Agent 6 — LoggingAgent

Nhiệm vụ:

- Lưu trace từng agent.
- Phục vụ màn Nhật ký Agent.
```

## F3. Tạo `docs/pytorch_award_notes.md`

```md
# PyTorch Award Notes

## Vì sao dự án có PyTorch thật?

Hệ thống không chỉ gọi LLM/API ngoài. Phần lõi nhận diện ảnh cây trồng sử dụng model vision chạy bằng PyTorch thông qua HuggingFace/transformers.

## Thành phần PyTorch

- Framework: PyTorch
- Model baseline: ResNet50/EfficientNet/MobileNet pretrained cho plant disease classification
- Input: ảnh lá cây
- Output: top-3 disease predictions

## Điểm có thể trình bày

1. Có model inference thật.
2. Có pipeline tiền xử lý ảnh.
3. Có top-k prediction.
4. Có khả năng bổ sung Grad-CAM.
5. Có thể fine-tune bằng PlantVillage/PlantDoc ở phase sau.
6. Có thể export ONNX/TorchScript nếu cần triển khai edge.

## Không nói quá

Không nói:

- “Team đã train model lớn từ đầu” nếu chưa train.
- “Độ chính xác 99% ngoài thực tế” nếu chỉ dùng PlantVillage/pretrained.

Nên nói:

- “Hiện tại dùng PyTorch pretrained baseline để chạy end-to-end trước.”
- “Phase sau fine-tune trên dataset phù hợp địa phương và đánh giá ngoài miền.”
```

---

# PHẦN G — Người 2 tạo Postman collection

Tạo `postman/CropDoctor_AI.postman_collection.json`:

```json
{
  "info": {
    "name": "CropDoctor AI",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Mock API",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8001/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8001",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Analyze Mock API",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "image",
              "type": "file",
              "src": []
            },
            {
              "key": "crop_type",
              "value": "Ớt",
              "type": "text"
            },
            {
              "key": "location",
              "value": "Đồng Nai",
              "type": "text"
            },
            {
              "key": "notes",
              "value": "Lá xuất hiện đốm sau mưa",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8001/api/analyze",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8001",
          "path": ["api", "analyze"]
        }
      }
    },
    {
      "name": "Analyze Real API",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "image",
              "type": "file",
              "src": []
            },
            {
              "key": "crop_type",
              "value": "Ớt",
              "type": "text"
            },
            {
              "key": "location",
              "value": "Đồng Nai",
              "type": "text"
            },
            {
              "key": "notes",
              "value": "Lá xuất hiện đốm sau mưa",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:8000/api/analyze",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "analyze"]
        }
      }
    }
  ]
}
```

---

# PHẦN H — Merge guide

Tạo `docs/merge_guide.md`:

```md
# Merge Guide — CropDoctor AI 2 người

## 1. Trước khi merge

Người 1 phải chạy được:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Người 2 phải chạy được:

```bash
uvicorn mock_server.main:app --host 0.0.0.0 --port 8001 --reload
pytest api/tests/test_schema_contract.py -q
```

## 2. Test mock trước

```bash
python api/scripts/smoke_test.py \
  --url http://localhost:8001/api/analyze \
  --image demo_assets/images/test.jpg
```

## 3. Test API thật

```bash
python api/scripts/smoke_test.py \
  --url http://localhost:8000/api/analyze \
  --image demo_assets/images/test.jpg
```

## 4. So sánh response

Cần kiểm tra các key này đều tồn tại:

```text
request_id
status
demo_mode
input
image_quality
vision
reasoning
recommendation
follow_up_questions
agent_logs
created_at
```

## 5. Lỗi thường gặp

### Lỗi 1: FE đọc key không tồn tại

Cách xử lý:

- Không sửa FE trước.
- Sửa API response để đúng schema.

### Lỗi 2: Model lỗi làm API chết

Cách xử lý:

- Bọc try/except ở vision_service.
- Nếu lỗi, trả top_predictions mock và status warning.

### Lỗi 3: DeepSeek lỗi quota/API key

Cách xử lý:

- Fallback sang rule-based reasoning.
- Không để toàn bộ endpoint chết.

### Lỗi 4: Response tiếng Anh quá nhiều

Cách xử lý:

- Thêm label_vi.
- Reasoning và recommendation luôn tiếng Việt.

## 6. Tiêu chí merge thành công

```text
[ ] /health chạy.
[ ] /api/analyze nhận ảnh và trả JSON.
[ ] Response đúng schema.
[ ] FE hiển thị được top_predictions.
[ ] FE hiển thị được final_diagnosis.
[ ] FE hiển thị được agent_logs.
[ ] Có ít nhất 2 demo case chạy được.
[ ] Có fallback nếu model/LLM lỗi.
```
```

---

# PHẦN I — Timeline làm song song trong 2 ngày

## Ngày 1 — Buổi sáng

### Người 1

```text
[ ] Dựng FastAPI thật.
[ ] Cài model dependencies.
[ ] Load model thử trong notebook/script riêng.
[ ] Tạo endpoint /health.
```

### Người 2

```text
[ ] Tạo contracts/*.schema.json.
[ ] Tạo mock_analyze_responses.json.
[ ] Tạo mock_server/main.py.
[ ] Chạy mock API ở port 8001.
```

Điểm ghép cuối buổi sáng:

```text
FE/BE có thể gọi mock API trước.
Người 1 chưa xong model cũng không ảnh hưởng.
```

## Ngày 1 — Buổi chiều

### Người 1

```text
[ ] vision_service.py trả top-3 prediction.
[ ] image_quality_service.py trả score.
[ ] Endpoint /api/analyze ghép vision + quality.
```

### Người 2

```text
[ ] Viết smoke_test.py.
[ ] Viết test_schema_contract.py.
[ ] Tạo Postman collection.
[ ] Gom 3-5 ảnh demo vào demo_assets/images.
```

Điểm ghép cuối ngày 1:

```text
Mock API chắc chắn chạy.
API thật nếu chưa xong vẫn không sao.
Đã có test để kiểm tra khi API thật xong.
```

## Ngày 2 — Buổi sáng

### Người 1

```text
[ ] deepseek_service.py gọi DeepSeek.
[ ] reasoning_service.py fallback nếu DeepSeek lỗi.
[ ] safety_service.py tạo IPM steps.
[ ] logging_service.py ghi agent logs.
```

### Người 2

```text
[ ] Viết batch_test_images.py.
[ ] Tạo docs/demo_script.md.
[ ] Tạo docs/ai_architecture.md.
[ ] Tạo docs/pytorch_award_notes.md.
```

Điểm ghép cuối buổi sáng:

```text
Người 2 test API thật bằng smoke_test.py.
Nếu API thật lỗi, demo vẫn dùng mock.
```

## Ngày 2 — Buổi chiều

### Người 1

```text
[ ] Fix lỗi endpoint thật.
[ ] Sinh sample_outputs/real_response_001.json.
[ ] Ghi model info vào docs/model_card.md.
```

### Người 2

```text
[ ] Chạy batch test với mock.
[ ] Chạy batch test với real API nếu có.
[ ] Chụp screenshot Swagger/Postman/terminal.
[ ] Hoàn thiện merge_guide.md và testing_report.md.
```

Điểm ghép cuối ngày 2:

```text
Có 2 đường demo:
1. Real API port 8000 nếu ổn.
2. Mock API port 8001 nếu real API chết sát giờ.
```

---

# PHẦN J — Definition of Done theo từng người

## Người 1 xong khi có đủ

```text
[ ] `uvicorn api.main:app --port 8000` chạy.
[ ] `/health` trả ok.
[ ] `/api/analyze` nhận ảnh và trả JSON.
[ ] Có top-3 prediction.
[ ] Có image_quality.
[ ] Có reasoning.
[ ] Có recommendation.
[ ] Có agent_logs.
[ ] Nếu DeepSeek lỗi vẫn có fallback.
[ ] Nếu model lỗi vẫn có DEMO_MODE fallback.
```

## Người 2 xong khi có đủ

```text
[ ] Mock API port 8001 chạy.
[ ] Contract schema có đủ.
[ ] Mock response validate qua schema.
[ ] smoke_test.py test được cả mock và real URL.
[ ] batch_test_images.py sinh CSV report.
[ ] Postman collection import được.
[ ] Có demo_cases.json.
[ ] Có demo_script.md.
[ ] Có ai_architecture.md.
[ ] Có pytorch_award_notes.md.
[ ] Có merge_guide.md.
```

---

# PHẦN K — Kịch bản cứu cháy nếu sát deadline

## Trường hợp 1: Người 1 chưa chạy được model

Dùng mock API của Người 2:

```text
FE gọi http://localhost:8001/api/analyze
```

Khi thuyết trình nói:

```text
Đây là mock integration mode để kiểm thử luồng agent và giao diện.
Core model PyTorch đang được thay vào cùng schema này.
```

Không nói dối là model đã chạy nếu chưa chạy.

## Trường hợp 2: Model chạy nhưng DeepSeek lỗi

Dùng rule-based reasoning:

```text
vision top-1
+ crop_type
+ notes
→ final_diagnosis đơn giản
```

Vẫn có agent logs:

```json
{
  "agent": "ReasoningAgent",
  "status": "done",
  "summary": "DeepSeek unavailable, used rule-based fallback.",
  "duration_ms": 20
}
```

## Trường hợp 3: FE lỗi sát giờ

Dùng Swagger hoặc Postman:

```text
http://localhost:8000/docs
http://localhost:8001/docs
```

Demo vẫn có upload ảnh, response JSON, agent logs.

## Trường hợp 4: Không có ảnh bệnh đẹp

Dùng ảnh bất kỳ nhưng response mock theo crop_type:

```text
crop_type=Ớt → trả case ớt
crop_type=Cà chua → trả case cà chua
```

Mục tiêu là demo flow trước, accuracy tính sau.

---

# PHẦN L — Bảng chia việc cực gọn để đưa vào nhóm

| Mảng việc | Người 1 | Người 2 | Ghép bằng gì |
|---|---|---|---|
| FastAPI thật | Chính | Test | `/api/analyze` |
| PyTorch model | Chính | Ghi report | `vision.top_predictions` |
| DeepSeek reasoning | Chính | Mock response | `reasoning` |
| Safety/IPM | Chính | Seed rule/data | `recommendation` |
| Agent logs | Chính format runtime | Mock + docs | `agent_logs` |
| JSON schema | Góp ý | Chính | `contracts/*.schema.json` |
| Mock API | Không cần | Chính | Port 8001 |
| Smoke test | Chạy | Chính | `api/scripts/smoke_test.py` |
| Demo cases | Góp ảnh thật | Chính | `demo_cases.json` |
| Report/docs | Góp model info | Chính | `docs/*.md` |
| Postman | Dùng | Chính | `postman/*.json` |

---

# PHẦN M — Thứ tự merge đề xuất

```text
1. Merge contract + mock + tests của Người 2 trước.
2. FE/BE cắm thử mock API.
3. Merge API thật của Người 1.
4. Chạy smoke_test với port 8000.
5. Nếu pass thì FE đổi sang port 8000.
6. Nếu fail thì demo dùng port 8001, sau đó fix tiếp.
```

Command:

```bash
git checkout main
git pull

git merge ai-integration-demo-package
pytest api/tests/test_schema_contract.py -q
uvicorn mock_server.main:app --port 8001 --reload

git merge ai-core-runner
uvicorn api.main:app --port 8000 --reload
python api/scripts/smoke_test.py --url http://localhost:8000/api/analyze --image demo_assets/images/test.jpg
```

---

# PHẦN N — Kết luận chốt cách làm

Người 1 tập trung làm **AI chạy thật**.  
Người 2 tập trung làm **mọi thứ giúp demo không chết**.

Cách này có lợi:

```text
- FE/BE không phải đợi model.
- Người 2 có việc rõ ràng, không bị thừa.
- Sát giờ demo vẫn có mock API cứu cháy.
- Khi model thật xong, chỉ thay port/API URL.
- Có schema/test/report nên nhìn chuyên nghiệp hơn.
```

Ưu tiên cuối cùng:

```text
1. Contract ổn định.
2. Mock API chạy.
3. Real API chạy.
4. Smoke test pass.
5. Demo script rõ.
6. Report có PyTorch angle.
```
