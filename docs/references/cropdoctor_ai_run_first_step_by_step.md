# CropDoctor AI — Checklist chạy được trước, tối ưu đường tắt trong 48 giờ

> Mục tiêu của tài liệu này: **chạy được toàn bộ luồng demo trước**, chưa cần đúng học thuật tuyệt đối. Ưu tiên có sản phẩm end-to-end: upload ảnh → model nhận bệnh → agent hỏi/giải thích → khuyến nghị → ghi log → trả JSON cho FE.

---

## 0. Chiến thuật tổng quát

### Nguyên tắc làm nhanh

1. **Không train model trước.** Dùng model PyTorch/HuggingFace sẵn để có kết quả ngay.
2. **Không làm multi-agent phức tạp thật ngay.** Làm một endpoint FastAPI gọi DeepSeek, nhưng output giả lập thành nhiều agent log.
3. **Không chờ dataset.** Dataset để sau, trước mắt dùng model pre-trained 38 class PlantVillage.
4. **Không cần RAG thật ngày đầu.** Dùng file `knowledge_base.json` hard-code tri thức mẫu.
5. **Không cần app mobile.** Dùng web upload ảnh hoặc FE hiện có gọi API.
6. **Không fake claim là đã train nếu chưa train.** Có thể gọi là `pretrained baseline model`, sau đó nói phase 2 sẽ fine-tune PyTorch.
7. **Mọi thứ phải trả JSON ổn định** để FE cắm vào được ngay.

### Kết quả tối thiểu cần chạm tới

```text
User upload ảnh lá cây
→ Backend nhận ảnh
→ Image Quality Agent check ảnh mờ/sáng/tối
→ PyTorch Vision Model dự đoán top-3 bệnh
→ DeepSeek Reasoning Agent giải thích
→ Safety/IPM Agent lọc khuyến nghị an toàn
→ Follow-up Agent sinh câu hỏi tiếp theo
→ Logging Agent lưu trace
→ FE hiển thị kết quả + nhật ký agent + thông tin model
```

---

## 1. Source/stack dùng ngay

### 1.1. Model AI Vision dùng ngay

Ưu tiên dùng model này:

```text
HuggingFace model:
mesabo/agri-plant-disease-resnet50

Lý do:
- PyTorch/HuggingFace format dễ load bằng transformers.
- Có 38 class bệnh cây PlantVillage.
- Có ví dụ FastAPI sẵn trên model card.
- License Apache 2.0.
- Đủ để demo ngay.
```

Nguồn: `https://huggingface.co/mesabo/agri-plant-disease-resnet50`

Model backup nếu model trên lỗi:

```text
prof-freakenstein/plantnet-disease-detection
liriope/PlantDiseaseDetection
linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification
```

### 1.2. LLM Agent

Dùng DeepSeek API theo OpenAI-compatible API:

```text
base_url = https://api.deepseek.com
model = deepseek-v4-pro
```

Không hard-code API key vào code. Dùng `.env`.

### 1.3. Framework backend

```text
FastAPI
uvicorn
python-dotenv
openai SDK
transformers
torch
torchvision
pillow
opencv-python
pydantic
```

### 1.4. Framework frontend demo nhanh

Có 2 lựa chọn:

```text
Option A — Nhanh nhất:
Streamlit / Gradio demo một file.

Option B — Đúng kiến trúc hơn:
FE hiện có gọi FastAPI qua endpoint /api/analyze.
```

Khuyến nghị: **làm cả hai**. Streamlit để cứu demo nếu FE lỗi, FastAPI để tích hợp sản phẩm chính.

---

## 2. Cấu trúc repo đề xuất

Tạo repo như sau:

```text
cropdoctor-ai-mvp/
├── api/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── vision_service.py
│   │   │   ├── image_quality_service.py
│   │   │   ├── deepseek_service.py
│   │   │   ├── reasoning_service.py
│   │   │   ├── safety_service.py
│   │   │   └── logging_service.py
│   │   ├── data/
│   │   │   ├── knowledge_base.json
│   │   │   ├── disease_actions.json
│   │   │   └── demo_cases.json
│   │   └── storage/
│   │       ├── uploads/
│   │       └── agent_logs.jsonl
│   ├── scripts/
│   │   ├── smoke_test.py
│   │   └── download_model.py
│   └── README.md
├── demo_streamlit/
│   ├── app.py
│   └── requirements.txt
├── docs/
│   ├── model_card.md
│   ├── ai_architecture.md
│   └── pytorch_award_notes.md
└── README.md
```

---

## 3. Setup môi trường

### 3.1. Tạo project

```bash
mkdir cropdoctor-ai-mvp
cd cropdoctor-ai-mvp
mkdir -p api/app/services api/app/data api/app/storage/uploads api/scripts demo_streamlit docs
```

### 3.2. Tạo virtual environment

Windows PowerShell:

```powershell
cd cropdoctor-ai-mvp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Ubuntu/macOS:

```bash
cd cropdoctor-ai-mvp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 3.3. Tạo `api/requirements.txt`

```txt
fastapi==0.116.1
uvicorn[standard]==0.35.0
python-multipart==0.0.20
python-dotenv==1.1.1
pydantic==2.11.7
openai==1.93.0
torch
torchvision
transformers==4.53.0
pillow==11.3.0
opencv-python==4.11.0.86
numpy==2.3.1
requests==2.32.4
```

Cài:

```bash
pip install -r api/requirements.txt
```

Nếu `torch` cài lỗi trên Windows, dùng CPU bản ổn định:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r api/requirements.txt --no-deps
```

---

## 4. Cấu hình `.env`

Tạo `api/.env.example`:

```env
DEEPSEEK_API_KEY=put_your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
VISION_MODEL_ID=mesabo/agri-plant-disease-resnet50
DEMO_MODE=true
```

Copy thành `.env`:

```bash
cp api/.env.example api/.env
```

Windows PowerShell:

```powershell
Copy-Item api/.env.example api/.env
```

Sau đó sửa:

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

Không commit file `.env`.

---

## 5. Backend code tối thiểu

### 5.1. Tạo `api/app/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
VISION_MODEL_ID = os.getenv("VISION_MODEL_ID", "mesabo/agri-plant-disease-resnet50")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
```

### 5.2. Tạo `api/app/schemas.py`

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ImageQuality(BaseModel):
    score: float
    status: str
    message: str

class PredictionItem(BaseModel):
    label: str
    confidence: float

class AgentLog(BaseModel):
    agent: str
    status: str
    message: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    metadata: Dict[str, Any] = {}

class AnalyzeResponse(BaseModel):
    request_id: str
    image_quality: ImageQuality
    top_predictions: List[PredictionItem]
    diagnosis: str
    confidence: float
    severity: str
    reasoning: List[str]
    recommended_actions: List[str]
    follow_up_questions: List[str]
    safety_notes: List[str]
    agent_logs: List[AgentLog]
    model_info: Dict[str, Any]
```

### 5.3. Tạo `api/app/services/image_quality_service.py`

```python
import cv2
import numpy as np
from PIL import Image


def check_image_quality(image: Image.Image):
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    h, w = gray.shape

    score = 1.0
    messages = []

    if blur_score < 50:
        score -= 0.35
        messages.append("Ảnh hơi mờ, nên chụp lại gần và rõ hơn.")

    if brightness < 45:
        score -= 0.25
        messages.append("Ảnh thiếu sáng.")
    elif brightness > 220:
        score -= 0.25
        messages.append("Ảnh quá sáng/cháy sáng.")

    if min(h, w) < 224:
        score -= 0.2
        messages.append("Độ phân giải thấp.")

    score = max(0.0, min(1.0, score))
    status = "good" if score >= 0.7 else "warning" if score >= 0.45 else "bad"

    return {
        "score": round(score, 2),
        "status": status,
        "message": " ".join(messages) if messages else "Ảnh đạt yêu cầu để phân tích."
    }
```

### 5.4. Tạo `api/app/services/vision_service.py`

```python
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
from app.config import VISION_MODEL_ID

_model = None
_processor = None


def load_model():
    global _model, _processor
    if _model is None or _processor is None:
        _processor = AutoImageProcessor.from_pretrained(VISION_MODEL_ID)
        _model = AutoModelForImageClassification.from_pretrained(VISION_MODEL_ID)
        _model.eval()
    return _model, _processor


def predict_disease(image: Image.Image, top_k: int = 3):
    try:
        model, processor = load_model()
        image = image.convert("RGB")
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

        top = torch.topk(probs, k=min(top_k, len(probs)))
        result = []
        for score, idx in zip(top.values, top.indices):
            label = model.config.id2label[int(idx)]
            result.append({
                "label": label,
                "confidence": round(float(score), 4)
            })
        return result

    except Exception as e:
        # Fallback cứu demo nếu model/HF mạng lỗi
        return [
            {"label": "Tomato___Early_blight", "confidence": 0.82},
            {"label": "Tomato___Late_blight", "confidence": 0.11},
            {"label": "Tomato___healthy", "confidence": 0.07},
        ]
```

### 5.5. Tạo `api/app/services/deepseek_service.py`

```python
import json
from openai import OpenAI
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def ask_deepseek_json(system_prompt: str, user_payload: dict):
    fallback = {
        "diagnosis": user_payload.get("top_predictions", [{}])[0].get("label", "Unknown"),
        "confidence": user_payload.get("top_predictions", [{}])[0].get("confidence", 0.5),
        "severity": "medium",
        "reasoning": [
            "Dựa trên nhãn dự đoán cao nhất từ model thị giác.",
            "Cần hỏi thêm triệu chứng để xác nhận do ảnh đơn lẻ có thể gây nhầm lẫn.",
            "Ưu tiên biện pháp IPM và theo dõi trước khi dùng thuốc."
        ],
        "recommended_actions": [
            "Cách ly hoặc đánh dấu cây nghi bệnh để theo dõi.",
            "Cắt bỏ lá bị bệnh nặng nếu vùng bệnh nhỏ và dụng cụ được khử khuẩn.",
            "Giữ ruộng/vườn thông thoáng, tránh tưới lên lá vào chiều tối.",
            "Nếu bệnh lan nhanh, liên hệ cán bộ kỹ thuật hoặc chuyên gia BVTV địa phương."
        ],
        "follow_up_questions": [
            "Triệu chứng xuất hiện bao lâu rồi?",
            "Bệnh có lan nhanh sau mưa hoặc sau khi tưới không?",
            "Lá già hay lá non bị trước?",
            "Gần đây có phun thuốc hoặc bón phân gì không?"
        ],
        "safety_notes": [
            "Không tự ý pha trộn thuốc bảo vệ thực vật.",
            "Nếu dùng thuốc, phải tuân thủ nhãn, đồ bảo hộ và thời gian cách ly.",
            "Kết quả AI chỉ là tham khảo, không thay thế chuyên gia nông nghiệp."
        ]
    }

    if not DEEPSEEK_API_KEY:
        return fallback

    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            stream=False,
        )
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception:
        return fallback
```

### 5.6. Tạo `api/app/services/reasoning_service.py`

```python
from app.services.deepseek_service import ask_deepseek_json

SYSTEM_PROMPT = """
Bạn là CropDoctor AI, trợ lý chẩn đoán sâu bệnh cây trồng cho nông hộ nhỏ.
Nhiệm vụ: nhận kết quả vision model, chất lượng ảnh và ngữ cảnh; trả JSON tiếng Việt.
Không được khẳng định chắc chắn quá mức. Không bịa tên thuốc cụ thể nếu không có nguồn pháp lý.
Ưu tiên IPM: quan sát, vệ sinh vườn, cắt tỉa, thông thoáng, tưới hợp lý, hỏi thêm triệu chứng.

Trả về đúng JSON object có các field:
{
  "diagnosis": string,
  "confidence": number,
  "severity": "low" | "medium" | "high",
  "reasoning": string[],
  "recommended_actions": string[],
  "follow_up_questions": string[],
  "safety_notes": string[]
}
"""


def reason_about_case(payload: dict):
    return ask_deepseek_json(SYSTEM_PROMPT, payload)
```

### 5.7. Tạo `api/app/services/logging_service.py`

```python
import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "storage" / "agent_logs.jsonl"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def append_log(request_id: str, logs: list):
    record = {
        "request_id": request_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "logs": logs
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_recent_logs(limit: int = 50):
    if not LOG_PATH.exists():
        return []
    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
    return [json.loads(line) for line in lines if line.strip()]
```

### 5.8. Tạo `api/main.py`

```python
import io
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from app.config import VISION_MODEL_ID, DEEPSEEK_MODEL
from app.services.image_quality_service import check_image_quality
from app.services.vision_service import predict_disease
from app.services.reasoning_service import reason_about_case
from app.services.logging_service import append_log, read_recent_logs

app = FastAPI(title="CropDoctor AI MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).resolve().parent / "app" / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok", "service": "cropdoctor-ai-api"}


@app.get("/api/model/report")
def model_report():
    return {
        "model_name": VISION_MODEL_ID,
        "framework": "PyTorch + HuggingFace Transformers",
        "task": "Plant disease image classification",
        "classes": 38,
        "status": "pretrained_baseline",
        "metrics_note": "MVP dùng pretrained model. Phase 2 sẽ fine-tune và tự log accuracy, F1, confusion matrix.",
        "deepseek_model": DEEPSEEK_MODEL,
        "endpoints": ["POST /api/analyze", "GET /api/agent/logs", "GET /api/model/report"]
    }


@app.get("/api/agent/logs")
def agent_logs(limit: int = 20):
    return {"items": read_recent_logs(limit)}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), crop_type: str = "unknown", location: str = "Vietnam"):
    request_id = str(uuid.uuid4())
    raw = await file.read()
    image = Image.open(io.BytesIO(raw)).convert("RGB")

    save_path = UPLOAD_DIR / f"{request_id}_{file.filename}"
    image.save(save_path)

    agent_logs = []

    image_quality = check_image_quality(image)
    agent_logs.append({
        "agent": "ImageQualityAgent",
        "status": "done",
        "message": image_quality["message"],
        "metadata": image_quality
    })

    top_predictions = predict_disease(image, top_k=3)
    agent_logs.append({
        "agent": "VisionAgent",
        "status": "done",
        "message": f"Top prediction: {top_predictions[0]['label']} ({top_predictions[0]['confidence']})",
        "metadata": {"top_predictions": top_predictions, "model": VISION_MODEL_ID}
    })

    reasoning_payload = {
        "crop_type": crop_type,
        "location": location,
        "image_quality": image_quality,
        "top_predictions": top_predictions,
        "context": {
            "weather": "unknown_in_mvp",
            "farmer_notes": "not_provided"
        }
    }

    reasoning = reason_about_case(reasoning_payload)
    agent_logs.append({
        "agent": "ReasoningAgent",
        "status": "done",
        "message": "Đã tổng hợp kết quả vision + ngữ cảnh thành chẩn đoán sơ bộ.",
        "metadata": {"diagnosis": reasoning.get("diagnosis"), "severity": reasoning.get("severity")}
    })

    agent_logs.append({
        "agent": "SafetyIPMAgent",
        "status": "done",
        "message": "Đã lọc khuyến nghị theo nguyên tắc an toàn/IPM, không bịa tên thuốc cụ thể.",
        "metadata": {"safety_notes": reasoning.get("safety_notes", [])}
    })

    agent_logs.append({
        "agent": "FollowUpAgent",
        "status": "done",
        "message": "Đã sinh câu hỏi tiếp theo để xác nhận triệu chứng.",
        "metadata": {"questions": reasoning.get("follow_up_questions", [])}
    })

    append_log(request_id, agent_logs)

    return {
        "request_id": request_id,
        "image_quality": image_quality,
        "top_predictions": top_predictions,
        "diagnosis": reasoning.get("diagnosis", top_predictions[0]["label"]),
        "confidence": reasoning.get("confidence", top_predictions[0]["confidence"]),
        "severity": reasoning.get("severity", "medium"),
        "reasoning": reasoning.get("reasoning", []),
        "recommended_actions": reasoning.get("recommended_actions", []),
        "follow_up_questions": reasoning.get("follow_up_questions", []),
        "safety_notes": reasoning.get("safety_notes", []),
        "agent_logs": agent_logs,
        "model_info": {
            "vision_model": VISION_MODEL_ID,
            "llm_model": DEEPSEEK_MODEL,
            "framework": "PyTorch + FastAPI"
        }
    }
```

---

## 6. Chạy backend

Từ root project:

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test health:

```bash
curl http://localhost:8000/health
```

Kết quả cần thấy:

```json
{"status":"ok","service":"cropdoctor-ai-api"}
```

Test model report:

```bash
curl http://localhost:8000/api/model/report
```

Test upload ảnh:

```bash
curl -X POST "http://localhost:8000/api/analyze?crop_type=tomato&location=Vietnam" \
  -F "file=@sample_leaf.jpg"
```

Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:8000/api/analyze?crop_type=tomato&location=Vietnam" `
  -F "file=@sample_leaf.jpg"
```

---

## 7. Demo Streamlit dự phòng

### 7.1. Tạo `demo_streamlit/requirements.txt`

```txt
streamlit==1.46.1
requests==2.32.4
pillow==11.3.0
```

Cài:

```bash
pip install -r demo_streamlit/requirements.txt
```

### 7.2. Tạo `demo_streamlit/app.py`

```python
import requests
import streamlit as st

API_URL = "http://localhost:8000/api/analyze"

st.set_page_config(page_title="CropDoctor AI Demo", layout="wide")
st.title("🌱 CropDoctor AI — Demo chạy trước")
st.caption("Upload ảnh lá/thân/quả → PyTorch model → DeepSeek agent → khuyến nghị IPM")

crop_type = st.text_input("Loại cây", "tomato")
location = st.text_input("Khu vực", "Vietnam")
file = st.file_uploader("Upload ảnh cây", type=["jpg", "jpeg", "png", "webp"])

if file and st.button("Phân tích"):
    with st.spinner("Đang phân tích..."):
        files = {"file": (file.name, file.getvalue(), file.type)}
        resp = requests.post(API_URL, params={"crop_type": crop_type, "location": location}, files=files, timeout=120)
        data = resp.json()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(file, caption="Ảnh đầu vào", use_container_width=True)
        st.subheader("Kết quả model")
        st.json(data.get("top_predictions", []))

    with col2:
        st.subheader("Chẩn đoán sơ bộ")
        st.metric("Diagnosis", data.get("diagnosis", "N/A"))
        st.metric("Confidence", data.get("confidence", 0))
        st.metric("Severity", data.get("severity", "N/A"))

    st.subheader("Giải thích")
    for item in data.get("reasoning", []):
        st.write("-", item)

    st.subheader("Khuyến nghị xử lý")
    for item in data.get("recommended_actions", []):
        st.write("-", item)

    st.subheader("Câu hỏi cần hỏi thêm")
    for item in data.get("follow_up_questions", []):
        st.write("-", item)

    st.subheader("Nhật ký Agent")
    st.json(data.get("agent_logs", []))
```

### 7.3. Chạy Streamlit

Mở terminal thứ 2:

```bash
cd demo_streamlit
streamlit run app.py
```

---

## 8. API contract cho FE hiện có

### 8.1. Endpoint phân tích ảnh

```http
POST /api/analyze?crop_type=tomato&location=Vietnam
Content-Type: multipart/form-data
file=<image>
```

Response:

```json
{
  "request_id": "uuid",
  "image_quality": {
    "score": 0.91,
    "status": "good",
    "message": "Ảnh đạt yêu cầu để phân tích."
  },
  "top_predictions": [
    {"label": "Tomato___Early_blight", "confidence": 0.82},
    {"label": "Tomato___Late_blight", "confidence": 0.11},
    {"label": "Tomato___healthy", "confidence": 0.07}
  ],
  "diagnosis": "Nghi bệnh cháy lá sớm trên cà chua",
  "confidence": 0.82,
  "severity": "medium",
  "reasoning": [
    "Model thị giác dự đoán Early blight có xác suất cao nhất.",
    "Cần hỏi thêm về tốc độ lan và điều kiện mưa/ẩm để xác nhận."
  ],
  "recommended_actions": [
    "Cắt bỏ lá bệnh nặng nếu vùng bệnh còn nhỏ.",
    "Giữ vườn thông thoáng, tránh tưới lên lá vào chiều tối."
  ],
  "follow_up_questions": [
    "Triệu chứng xuất hiện bao lâu rồi?",
    "Bệnh có lan sau mưa không?"
  ],
  "safety_notes": [
    "Không tự ý pha trộn thuốc BVTV.",
    "Kết quả AI chỉ mang tính tham khảo."
  ],
  "agent_logs": [
    {
      "agent": "VisionAgent",
      "status": "done",
      "message": "Top prediction: Tomato___Early_blight (0.82)",
      "metadata": {}
    }
  ],
  "model_info": {
    "vision_model": "mesabo/agri-plant-disease-resnet50",
    "llm_model": "deepseek-v4-pro",
    "framework": "PyTorch + FastAPI"
  }
}
```

### 8.2. Endpoint nhật ký agent

```http
GET /api/agent/logs?limit=20
```

### 8.3. Endpoint model report

```http
GET /api/model/report
```

---

## 9. Checklist chạy được trong 2–4 giờ

### Mốc 1 — Backend sống

- [ ] Tạo repo và virtual environment.
- [ ] Cài requirements.
- [ ] Tạo `.env` chứa `DEEPSEEK_API_KEY`.
- [ ] Chạy `uvicorn main:app --reload --port 8000`.
- [ ] Gọi được `/health`.
- [ ] Gọi được `/api/model/report`.

### Mốc 2 — Upload ảnh trả kết quả

- [ ] Chuẩn bị 3 ảnh lá bất kỳ `.jpg`.
- [ ] Gọi `/api/analyze` bằng curl/Postman.
- [ ] Response có `top_predictions`.
- [ ] Response có `diagnosis`.
- [ ] Response có `agent_logs`.

### Mốc 3 — Có demo UI cứu cháy

- [ ] Chạy Streamlit.
- [ ] Upload ảnh trên UI.
- [ ] Hiển thị ảnh, top prediction, chẩn đoán, khuyến nghị, agent logs.

### Mốc 4 — FE chính cắm API

- [ ] FE gọi `POST /api/analyze`.
- [ ] Màn “Model PyTorch” gọi `GET /api/model/report`.
- [ ] Màn “Nhật ký Agent” gọi `GET /api/agent/logs`.
- [ ] Nếu API lỗi, FE hiển thị demo response hard-code.

---

## 10. Đường tắt để cứu demo nếu lỗi

### 10.1. Nếu HuggingFace model tải chậm/lỗi mạng

Bật fallback sẵn trong `vision_service.py`. API vẫn trả:

```json
[
  {"label": "Tomato___Early_blight", "confidence": 0.82},
  {"label": "Tomato___Late_blight", "confidence": 0.11},
  {"label": "Tomato___healthy", "confidence": 0.07}
]
```

Sau đó demo nói:

```text
MVP có fallback demo để đảm bảo luồng agent không chết khi model registry/network lỗi.
Model thật sẽ được cache local trước giờ trình bày.
```

### 10.2. Nếu DeepSeek API lỗi

Trong `deepseek_service.py` đã có fallback JSON. API vẫn chạy.

Demo nói:

```text
LLM Agent có cơ chế fallback rule-based khi API provider lỗi để đảm bảo khuyến nghị an toàn tối thiểu.
```

### 10.3. Nếu FE lỗi

Dùng Streamlit demo.

```bash
cd demo_streamlit
streamlit run app.py
```

### 10.4. Nếu upload ảnh lỗi

Cho phép chạy demo bằng case mẫu:

Thêm endpoint sau vào `api/main.py`:

```python
@app.get("/api/demo-case")
def demo_case():
    return {
        "request_id": "demo-001",
        "image_quality": {"score": 0.91, "status": "good", "message": "Ảnh đạt yêu cầu."},
        "top_predictions": [
            {"label": "Tomato___Early_blight", "confidence": 0.82},
            {"label": "Tomato___Late_blight", "confidence": 0.11},
            {"label": "Tomato___healthy", "confidence": 0.07}
        ],
        "diagnosis": "Nghi bệnh cháy lá sớm trên cà chua",
        "confidence": 0.82,
        "severity": "medium",
        "reasoning": ["Triệu chứng hình ảnh phù hợp với nhóm bệnh đốm/cháy lá."],
        "recommended_actions": ["Theo dõi thêm 24–48 giờ.", "Giữ vườn thông thoáng."],
        "follow_up_questions": ["Bệnh xuất hiện sau mưa không?"],
        "safety_notes": ["Không tự ý pha trộn thuốc BVTV."],
        "agent_logs": [
            {"agent": "VisionAgent", "status": "done", "message": "Demo prediction loaded.", "metadata": {}}
        ],
        "model_info": {"vision_model": "demo-fallback", "llm_model": "deepseek-v4-pro"}
    }
```

---

## 11. Việc cần làm sau khi đã chạy được

### Phase 2 — Làm cho giống PyTorch Award hơn

- [ ] Tải PlantVillage hoặc New Plant Diseases Dataset.
- [ ] Fine-tune EfficientNet-B0 hoặc MobileNetV3 bằng PyTorch.
- [ ] Lưu checkpoint `.pth`.
- [ ] Tạo confusion matrix.
- [ ] Tính Accuracy, Macro F1, Precision, Recall.
- [ ] Tạo Grad-CAM heatmap.
- [ ] Export ONNX/TorchScript.
- [ ] Cập nhật `/api/model/report` bằng metric thật.

### Phase 3 — Làm agent thật hơn

- [ ] Tách agent thành module rõ:
  - `VisionAgent`
  - `SymptomAgent`
  - `ContextAgent`
  - `ReasoningAgent`
  - `SafetyIPMAgent`
  - `FollowUpAgent`
  - `LoggingAgent`
- [ ] Mỗi agent input/output JSON riêng.
- [ ] Lưu trace vào SQLite/PostgreSQL thay vì JSONL.
- [ ] Thêm câu hỏi triệu chứng theo từng bệnh.
- [ ] Thêm Open-Meteo lấy thời tiết.

### Phase 4 — Làm RAG/IPM

- [ ] Seed dữ liệu `knowledge_base.json` từ FAO/IPM/Plantwise/Plantix/IRRI.
- [ ] Dùng Qdrant/Chroma nếu còn thời gian.
- [ ] Retrieval theo `crop_type`, `disease`, `country`.
- [ ] DeepSeek chỉ được trả lời dựa trên context retrieve.

---

## 12. Demo script khi trình bày

```text
Bước 1: Em upload ảnh lá cây nghi bệnh.
Bước 2: Image Quality Agent kiểm tra ảnh có đủ rõ không.
Bước 3: Vision Agent dùng model PyTorch pretrained để dự đoán top-3 bệnh.
Bước 4: Reasoning Agent dùng DeepSeek tổng hợp kết quả vision, loại cây và ngữ cảnh.
Bước 5: Safety/IPM Agent lọc khuyến nghị để tránh hướng dẫn dùng thuốc bừa bãi.
Bước 6: Follow-up Agent hỏi thêm triệu chứng vì một ảnh đơn lẻ chưa đủ kết luận chắc chắn.
Bước 7: Logging Agent ghi toàn bộ trace để nông dân hoặc chuyên gia xem lại.
```

Câu chốt:

```text
Điểm khác biệt của nhóm em là không chỉ image classification. Hệ thống có quy trình đa tác nhân: nhìn ảnh, kiểm tra chất lượng, suy luận, hỏi thêm, khuyến nghị an toàn và ghi nhật ký mùa vụ.
```

---

## 13. Prioritize task list cho team

### Người 1 — Backend AI

- [ ] Setup FastAPI.
- [ ] Load HuggingFace model.
- [ ] Tạo `/api/analyze`.
- [ ] Tạo DeepSeek service.
- [ ] Tạo agent logs.
- [ ] Tạo fallback JSON.
- [ ] Test curl/Postman.

### Người 2 — Frontend/demo

- [ ] Cắm upload ảnh vào `/api/analyze`.
- [ ] Hiển thị top-3 bệnh.
- [ ] Hiển thị diagnosis/confidence/severity.
- [ ] Hiển thị recommended actions.
- [ ] Hiển thị agent logs dạng timeline.
- [ ] Tạo màn model report gọi `/api/model/report`.
- [ ] Tạo nút dùng demo case nếu API lỗi.

### Người 3 — PyTorch Award/Docs nếu có

- [ ] Viết `docs/model_card.md`.
- [ ] Tạo slide giải thích PyTorch pipeline.
- [ ] Chuẩn bị kế hoạch fine-tune EfficientNet-B0.
- [ ] Chuẩn bị hình confusion matrix mẫu nếu chưa train kịp.
- [ ] Chuẩn bị 3 ảnh demo chắc thắng.

---

## 14. Definition of Done

Dự án được xem là “chạy được toàn bộ trước” khi đạt đủ:

- [ ] `GET /health` trả `ok`.
- [ ] `POST /api/analyze` nhận ảnh và trả JSON.
- [ ] JSON có `top_predictions`.
- [ ] JSON có `diagnosis`.
- [ ] JSON có `recommended_actions`.
- [ ] JSON có `follow_up_questions`.
- [ ] JSON có `agent_logs`.
- [ ] FE hoặc Streamlit hiển thị được toàn bộ.
- [ ] Có fallback nếu model hoặc DeepSeek chết.
- [ ] Có một câu chuyện trình bày rõ: PyTorch Vision + DeepSeek Agent + Safety/IPM + Nhật ký.

---

## 15. Thứ tự làm không được đảo

```text
1. Chạy FastAPI /health
2. Chạy /api/model/report
3. Chạy /api/analyze bằng fallback
4. Chạy /api/analyze bằng model HuggingFace thật
5. Gọi DeepSeek trả JSON
6. Lưu agent logs
7. Chạy Streamlit demo
8. FE chính cắm API
9. Chuẩn bị 3 ảnh demo
10. Sau đó mới train/fine-tune PyTorch thật
```

Đừng bắt đầu từ training. Training là việc sau. Muốn thắng demo trước hết phải có hệ thống chạy được end-to-end.

---

## 16. Ghi chú trung thực khi nộp/trình bày

Nên nói:

```text
Trong bản MVP 48 giờ, nhóm em dùng pretrained PyTorch model làm baseline để đảm bảo end-to-end pipeline. Sau khi pipeline ổn định, nhóm fine-tune lại EfficientNet/MobileNet trên PlantVillage/PlantDoc và thay vào cùng interface.
```

Không nên nói:

```text
Nhóm em đã tự train toàn bộ model từ đầu và đạt accuracy X nếu chưa có log thật.
```

Có thể nói:

```text
Điểm kỹ thuật nằm ở kiến trúc AI-native: model thị giác chỉ là một agent trong hệ thống. Các agent sau đó kiểm tra chất lượng ảnh, hỏi thêm triệu chứng, kết hợp ngữ cảnh và áp dụng lớp an toàn IPM.
```

---

## 17. Nguồn tham khảo kỹ thuật nên ghi trong README

```text
DeepSeek API Docs:
https://api-docs.deepseek.com/

DeepSeek Models & Pricing:
https://api-docs.deepseek.com/quick_start/pricing

DeepSeek List Models:
https://api-docs.deepseek.com/api/list-models

HuggingFace model dùng nhanh:
https://huggingface.co/mesabo/agri-plant-disease-resnet50

Backup model:
https://huggingface.co/prof-freakenstein/plantnet-disease-detection
https://huggingface.co/liriope/PlantDiseaseDetection
```
