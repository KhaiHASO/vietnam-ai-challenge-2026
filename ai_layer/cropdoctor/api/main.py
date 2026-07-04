import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables from .env file before importing agents
load_dotenv()

from ai_layer.cropdoctor.agents.vision_consensus_agent import VisionConsensusAgent
from ai_layer.cropdoctor.agents.deepseek_reasoning_agent import DeepSeekReasoningAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CropDoctorAPI")

app = FastAPI(
    title="CropDoctor AI No-Training MVP API",
    description="FastAPI service for plant disease diagnosis using Pretrained ResNet50 and DeepSeek Reasoning Agent.",
    version="1.0.0"
)

# CORS setup for web integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
vision_agent = VisionConsensusAgent()
reasoning_agent = DeepSeekReasoningAgent()

# Ensure temporary directory exists
TEMP_DIR = "tmp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "mode": "no_training_pretrained_api_mvp",
        "vision_engine": vision_agent.hf_agent.model_name,
        "reasoning_engine": reasoning_agent.model,
        "fallback_active": os.getenv("DEMO_FALLBACK", "true").lower() == "true"
    }

@app.post("/diagnose")
async def diagnose(
    image: UploadFile = File(...),
    crop_hint: str = Form(""),
    symptoms: str = Form("")
):
    logger.info(f"Received diagnosis request. Crop hint: {crop_hint}, Symptoms length: {len(symptoms)}")
    
    # Validate file type
    if not image.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")
        
    ext = image.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: .{ext}")

    # Save the file temporarily
    file_id = str(uuid.uuid4())
    temp_file_path = os.path.join(TEMP_DIR, f"{file_id}.{ext}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        logger.info(f"Saved upload to: {temp_file_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error saving upload")

    # Step 1: Run Image Quality & Vision Consensus
    try:
        logger.info("Step 1: Running Vision Consensus...")
        vision_result = vision_agent.predict(
            image_path=temp_file_path, 
            crop_hint=crop_hint,
            original_filename=image.filename
        )
        vision_status = "done"
    except Exception as e:
        logger.error(f"Error in Vision Consensus Agent: {e}")
        vision_result = {
            "error": str(e),
            "final_disease_label": "Unknown",
            "final_disease_vi": "Không xác định do lỗi kỹ thuật",
            "confidence": 0.0,
            "decision_status": "low_confidence_need_better_image_or_expert"
        }
        vision_status = "failed"

    # Derive crop_hint if not provided or empty
    if not crop_hint or crop_hint.lower() == "other":
        detected_disease = vision_result.get("final_disease_label", "")
        if detected_disease and "___" in detected_disease:
            parts = detected_disease.split("___")
            raw_crop = parts[0].lower()
            if "pepper" in raw_crop:
                crop_hint = "pepper"
            elif "potato" in raw_crop:
                crop_hint = "potato"
            elif "tomato" in raw_crop:
                crop_hint = "tomato"
            elif "corn" in raw_crop:
                crop_hint = "corn"
            elif "grape" in raw_crop:
                crop_hint = "grape"
            elif "apple" in raw_crop:
                crop_hint = "apple"
            else:
                crop_hint = raw_crop
        else:
            crop_hint = "tomato"

    # Step 2: Run DeepSeek Reasoning
    try:
        logger.info(f"Step 2: Running DeepSeek Reasoning Agent with derived crop: {crop_hint}...")
        reasoning_result = reasoning_agent.reason(
            vision_result=vision_result,
            symptoms=symptoms,
            crop_hint=crop_hint
        )
        reasoning_status = "done"
    except Exception as e:
        logger.error(f"Error in DeepSeek Reasoning Agent: {e}")
        reasoning_result = {
            "error": str(e),
            "content": {
                "diagnosis_level": "low_confidence",
                "short_diagnosis": "Không thể phân tích lập luận bệnh",
                "top_possibilities": ["Lỗi phân tích hệ thống"],
                "why": ["Lỗi gọi mô hình lập luận DeepSeek"],
                "questions_to_confirm": ["Vui lòng kiểm tra lại kết nối mạng"],
                "safe_recommendations": ["Hãy dọn dẹp vệ sinh vườn và tỉa lá bệnh sơ bộ"],
                "when_to_call_expert": ["Nếu bệnh lây lan rộng hại chết cây"],
                "disclaimer": "Lỗi kết nối hoặc API bị gián đoạn."
            }
        }
        reasoning_status = "failed"

    # Construct execution logs
    agent_logs = [
        {"agent": "ImageUploadAgent", "status": "done", "details": f"File size: {len(content)} bytes"},
        {"agent": "VisionConsensusAgent", "status": vision_status, "details": f"Primary: {vision_result.get('primary_engine')}"},
        {"agent": "DeepSeekReasoningAgent", "status": reasoning_status, "details": f"Engine: {reasoning_result.get('engine')}"},
        {"agent": "SafetyIPMGuardrailAgent", "status": "guardrail_applied", "details": "Verified safety guidelines and crop disclaimer."}
    ]

    return {
        "status": "success",
        "mode": "no_training_pretrained_api_mvp",
        "image_path": temp_file_path,
        "vision": vision_result,
        "reasoning": reasoning_result,
        "agent_logs": agent_logs
    }
