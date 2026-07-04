import os
import logging
from typing import Dict, Any, List
from PIL import Image

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HFVisionAgent")

# Mapping PlantVillage 38 classes to Vietnamese names and descriptions
PLANT_VILLAGE_CLASSES_VI = {
    "Apple___Apple_scab": {"vi": "Táo - Bệnh ghẻ (Apple scab)", "crop": "apple"},
    "Apple___Black_rot": {"vi": "Táo - Bệnh thối đen (Black rot)", "crop": "apple"},
    "Apple___Cedar_apple_rust": {"vi": "Táo - Bệnh rỉ sắt táo Cedar", "crop": "apple"},
    "Apple___healthy": {"vi": "Táo - Khỏe mạnh", "crop": "apple"},
    "Blueberry___healthy": {"vi": "Việt quất - Khỏe mạnh", "crop": "blueberry"},
    "Cherry_(including_sour)___Powdery_mildew": {"vi": "Anh đào - Bệnh phấn trắng", "crop": "cherry"},
    "Cherry_(including_sour)___healthy": {"vi": "Anh đào - Khỏe mạnh", "crop": "cherry"},
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {"vi": "Ngô - Bệnh đốm lá xám (Cercospora)", "crop": "corn"},
    "Corn_(maize)___Common_rust_": {"vi": "Ngô - Bệnh rỉ sắt thông thường", "crop": "corn"},
    "Corn_(maize)___Northern_Leaf_Blight": {"vi": "Ngô - Bệnh cháy lá muộn (Northern Leaf Blight)", "crop": "corn"},
    "Corn_(maize)___healthy": {"vi": "Ngô - Khỏe mạnh", "crop": "corn"},
    "Grape___Black_rot": {"vi": "Nho - Bệnh thối đen (Black rot)", "crop": "grape"},
    "Grape___Esca_(Black_Measles)": {"vi": "Nho - Bệnh Esca (Lốm đốm đen)", "crop": "grape"},
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {"vi": "Nho - Bệnh cháy lá (Isariopsis)", "crop": "grape"},
    "Grape___healthy": {"vi": "Nho - Khỏe mạnh", "crop": "grape"},
    "Orange___Haunglongbing_(Citrus_greening)": {"vi": "Cam - Bệnh vàng lá gân xanh (Citrus greening)", "crop": "orange"},
    "Peach___Bacterial_spot": {"vi": "Đào - Bệnh đốm vi khuẩn", "crop": "peach"},
    "Peach___healthy": {"vi": "Đào - Khỏe mạnh", "crop": "peach"},
    "Pepper,_bell___Bacterial_spot": {"vi": "Ớt chuông - Bệnh đốm vi khuẩn", "crop": "pepper"},
    "Pepper,_bell___healthy": {"vi": "Ớt chuông - Khỏe mạnh", "crop": "pepper"},
    "Potato___Early_blight": {"vi": "Khoai tây - Bệnh úa sớm (Early blight)", "crop": "potato"},
    "Potato___Late_blight": {"vi": "Khoai tây - Bệnh mốc sương (Late blight)", "crop": "potato"},
    "Potato___healthy": {"vi": "Khoai tây - Khỏe mạnh", "crop": "potato"},
    "Raspberry___healthy": {"vi": "Mâm xôi - Khỏe mạnh", "crop": "raspberry"},
    "Soybean___healthy": {"vi": "Đậu nành - Khỏe mạnh", "crop": "soybean"},
    "Squash___Powdery_mildew": {"vi": "Bí ngòi/Bí đỏ - Bệnh phấn trắng", "crop": "squash"},
    "Strawberry___Leaf_scorch": {"vi": "Dâu tây - Bệnh cháy lá (Leaf scorch)", "crop": "strawberry"},
    "Strawberry___healthy": {"vi": "Dâu tây - Khỏe mạnh", "crop": "strawberry"},
    "Tomato___Bacterial_spot": {"vi": "Cà chua - Bệnh đốm vi khuẩn", "crop": "tomato"},
    "Tomato___Early_blight": {"vi": "Cà chua - Bệnh úa sớm (Early blight)", "crop": "tomato"},
    "Tomato___Late_blight": {"vi": "Cà chua - Bệnh mốc sương (Late blight)", "crop": "tomato"},
    "Tomato___Leaf_Mold": {"vi": "Cà chua - Bệnh mốc lá (Leaf mold)", "crop": "tomato"},
    "Tomato___Septoria_leaf_spot": {"vi": "Cà chua - Bệnh đốm lá Septoria", "crop": "tomato"},
    "Tomato___Spider_mites Two-spotted_spider_mite": {"vi": "Cà chua - Bệnh nhện đỏ hai chấm", "crop": "tomato"},
    "Tomato___Target_Spot": {"vi": "Cà chua - Bệnh đốm vòng (Target Spot)", "crop": "tomato"},
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {"vi": "Cà chua - Bệnh virus xoăn lùn lá vàng", "crop": "tomato"},
    "Tomato___Tomato_mosaic_virus": {"vi": "Cà chua - Bệnh virus khảm cà chua", "crop": "tomato"},
    "Tomato___healthy": {"vi": "Cà chua - Khỏe mạnh", "crop": "tomato"}
}

def standardize_label(label: str) -> str:
    s = label.strip()
    
    mapping = {
        "Tomato_Early_Blight": "Tomato___Early_blight",
        "Tomato_Late_Blight": "Tomato___Late_blight",
        "Tomato_Healthy": "Tomato___healthy",
        "Tomato_Bacterial_Spot": "Tomato___Bacterial_spot",
        "Tomato_Leaf_Mold": "Tomato___Leaf_Mold",
        "Tomato_Mosaic_Virus": "Tomato___Tomato_mosaic_virus",
        "Tomato_Septoria_Leaf_Spot": "Tomato___Septoria_leaf_spot",
        "Tomato_Spider_Mites": "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato_Target_Spot": "Tomato___Target_Spot",
        "Tomato_Yellow_Leaf_Curl_Virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Potato_Early_Blight": "Potato___Early_blight",
        "Potato_Late_Blight": "Potato___Late_blight",
        "Potato_Healthy": "Potato___healthy",
        "Pepper_Bacterial_Spot": "Pepper,_bell___Bacterial_spot",
        "Pepper_Healthy": "Pepper,_bell___healthy",
        "Apple_Scab": "Apple___Apple_scab",
        "Apple_Black_Rot": "Apple___Black_rot",
        "Apple_Cedar_Apple_Rust": "Apple___Cedar_apple_rust",
        "Apple_Healthy": "Apple___healthy",
        "Corn_Common_Rust": "Corn_(maize)___Common_rust_",
        "Corn_Gray_Leaf_Spot": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "Corn_Northern_Leaf_Blight": "Corn_(maize)___Northern_Leaf_Blight",
        "Corn_Healthy": "Corn_(maize)___healthy",
        "Grape_Black_Rot": "Grape___Black_rot",
        "Grape_Healthy": "Grape___healthy"
    }
    
    return mapping.get(s, s)

class PretrainedHFVisionAgent:
    def __init__(self):
        # Default to Alan04020/vit-plant-disease-v2 which loads correctly on Windows without config issues
        self.model_name = os.getenv("HF_PLANT_MODEL", "Alan04020/vit-plant-disease-v2")
        self.classifier = None
        self.initialized = False
        
        try:
            from transformers import pipeline
            import torch
            logger.info(f"Loading HF classification pipeline with model: {self.model_name}")
            device = 0 if torch.cuda.is_available() else -1
            self.classifier = pipeline("image-classification", model=self.model_name, device=device)
            self.initialized = True
            logger.info("HF Vision Model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize HF Vision model due to: {e}. Running in Fallback/Demo mode.")
            self.initialized = False

    def predict(self, image_path: str, top_k: int = 5, crop_hint: str = "", original_filename: str = "") -> Dict[str, Any]:
        if not os.path.exists(image_path):
            logger.error(f"Image path not found: {image_path}")
            return {
                "engine": "hf_pretrained_vit",
                "error": "Image file not found",
                "top_predictions": [],
                "best_prediction": None,
                "fallback_used": False
            }
            
        if not self.initialized:
            return {
                "engine": "hf_pretrained_vit",
                "error": "ViT model was not initialized successfully",
                "top_predictions": [],
                "best_prediction": None,
                "fallback_used": False
            }

        try:
            image = Image.open(image_path).convert("RGB")
            results = self.classifier(image, top_k=top_k)
            
            predictions: List[Dict[str, Any]] = []
            for item in results:
                raw_label = item.get("label")
                label = standardize_label(raw_label)
                score = float(item.get("score", 0.0))
                
                vi_detail = PLANT_VILLAGE_CLASSES_VI.get(label, {"vi": label, "crop": "unknown"})
                
                predictions.append({
                    "label": label,
                    "label_vi": vi_detail["vi"],
                    "crop": vi_detail["crop"],
                    "score": score,
                    "source": "hf_pretrained_vit"
                })
            
            predictions = sorted(predictions, key=lambda x: x["score"], reverse=True)
            
            return {
                "engine": "hf_pretrained_vit",
                "model": self.model_name,
                "top_predictions": predictions,
                "best_prediction": predictions[0] if predictions else None,
                "fallback_used": False
            }
            
        except Exception as e:
            logger.error(f"Error predicting with HF model: {e}. Falling back...")
            return self._mock_prediction(crop_hint, image_path, error=str(e), original_filename=original_filename)

    def _mock_prediction(self, crop_hint: str, image_path: str, error: str = "", original_filename: str = "") -> Dict[str, Any]:
        crop = (crop_hint or "tomato").lower()
        name_to_check = original_filename if original_filename else os.path.basename(image_path)
        image_name = name_to_check.lower()
        
        matched_class = None
        
        if "early_blight" in image_name:
            if "potato" in image_name or crop == "potato":
                matched_class = "Potato___Early_blight"
            else:
                matched_class = "Tomato___Early_blight"
        elif "late_blight" in image_name:
            if "potato" in image_name or crop == "potato":
                matched_class = "Potato___Late_blight"
            else:
                matched_class = "Tomato___Late_blight"
        elif "bacterial_spot" in image_name:
            if "pepper" in image_name or crop == "pepper":
                matched_class = "Pepper,_bell___Bacterial_spot"
            else:
                matched_class = "Tomato___Bacterial_spot"
        elif "rust" in image_name:
            matched_class = "Corn_(maize)___Common_rust_"
        elif "leaf_blight" in image_name:
            if "grape" in image_name:
                matched_class = "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"
            else:
                matched_class = "Corn_(maize)___Northern_Leaf_Blight"
        elif "healthy" in image_name:
            if crop == "tomato":
                matched_class = "Tomato___healthy"
            elif crop == "potato":
                matched_class = "Potato___healthy"
            elif crop == "corn":
                matched_class = "Corn_(maize)___healthy"
            else:
                matched_class = f"{crop.capitalize()}___healthy"
                
        if not matched_class:
            if crop == "tomato":
                matched_class = "Tomato___Early_blight"
            elif crop == "potato":
                matched_class = "Potato___Late_blight"
            elif crop == "pepper":
                matched_class = "Pepper,_bell___Bacterial_spot"
            elif crop == "corn":
                matched_class = "Corn_(maize)___Common_rust_"
            elif crop == "grape":
                matched_class = "Grape___Black_rot"
            elif crop == "apple":
                matched_class = "Apple___Apple_scab"
            else:
                matched_class = "Tomato___Early_blight"

        vi_detail = PLANT_VILLAGE_CLASSES_VI.get(matched_class, {"vi": matched_class, "crop": crop})
        
        other_classes = [k for k, v in PLANT_VILLAGE_CLASSES_VI.items() if v["crop"] == crop and k != matched_class][:3]
        if len(other_classes) < 2:
            other_classes += [k for k, v in PLANT_VILLAGE_CLASSES_VI.items() if k != matched_class][:3]
            
        predictions = [
            {
                "label": matched_class,
                "label_vi": vi_detail["vi"],
                "crop": vi_detail["crop"],
                "score": 0.88,
                "source": "demo_fallback"
            },
            {
                "label": other_classes[0],
                "label_vi": PLANT_VILLAGE_CLASSES_VI.get(other_classes[0], {"vi": other_classes[0]})["vi"],
                "crop": PLANT_VILLAGE_CLASSES_VI.get(other_classes[0], {"crop": crop})["crop"],
                "score": 0.08,
                "source": "demo_fallback"
            },
            {
                "label": other_classes[1],
                "label_vi": PLANT_VILLAGE_CLASSES_VI.get(other_classes[1], {"vi": other_classes[1]})["vi"],
                "crop": PLANT_VILLAGE_CLASSES_VI.get(other_classes[1], {"crop": crop})["crop"],
                "score": 0.03,
                "source": "demo_fallback"
            }
        ]
        
        return {
            "engine": "hf_pretrained_vit_fallback",
            "model": self.model_name,
            "top_predictions": predictions,
            "best_prediction": predictions[0],
            "fallback_used": True,
            "note": "Hugging Face model load failed or demo bypass enabled. Output generated from fallback engine.",
            "error_detail": error
        }
