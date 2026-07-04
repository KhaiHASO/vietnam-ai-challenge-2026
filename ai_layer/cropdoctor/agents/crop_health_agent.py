import os
import base64
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("CropHealthAgent")

MOCK_DISEASE_DETAILS = {
    "Tomato___Early_blight": {
        "disease_name": "Bệnh úa sớm cà chua (Early Blight)",
        "symptoms": "Đốm nâu đen có vòng tròn đồng tâm (như hình bia bắn), thường xuất hiện trước tiên ở các lá già bên dưới, sau đó lan dần lên trên. Lá bị úa vàng và rụng sớm.",
        "description": "Bệnh do nấm Alternaria solani gây ra, phát triển mạnh trong điều kiện nóng ẩm, mưa nhiều hoặc tưới nước lên lá.",
        "severity": "Trung bình đến Cao",
        "treatment": {
            "chemical": "Sử dụng thuốc gốc đồng (Copper hydroxide), Chlorothalonil hoặc Mancozeb khi bệnh vừa xuất hiện.",
            "biological": "Phun các chế phẩm sinh học chứa Trichoderma harzianum hoặc Bacillus subtilis.",
            "prevention": "Luân canh cây trồng, tỉa bỏ các lá già sát mặt đất, tưới nước vào gốc thay vì phun lên lá, chọn giống kháng bệnh."
        }
    },
    "Tomato___Late_blight": {
        "disease_name": "Bệnh mốc sương cà chua (Late Blight)",
        "symptoms": "Vết bệnh dạng úng nước màu xanh tái đến nâu đen ở mép hoặc đầu lá, lan rất nhanh. Mặt dưới lá có lớp tơ nấm màu trắng đục trong điều kiện ẩm ướt. Quả có vết lõm màu nâu, cứng.",
        "description": "Bệnh cực kỳ nguy hiểm do noãn nấm Phytophthora infestans gây ra, có khả năng lây lan nhanh chóng phá hủy toàn bộ ruộng cà chua chỉ trong vài ngày dưới điều kiện trời mát và ẩm thấp.",
        "severity": "Rất cao",
        "treatment": {
            "chemical": "Phun ngay thuốc đặc trị như Metalaxyl, Ridomil Gold, Mancozeb hoặc Cymoxanil.",
            "biological": "Sử dụng chế phẩm Bacillus subtilis để phòng ngừa sớm.",
            "prevention": "Tiêu hủy ngay cây bị bệnh nặng, mật độ trồng thưa thông thoáng, tránh trồng xen canh với khoai tây."
        }
    },
    "Potato___Early_blight": {
        "disease_name": "Bệnh úa sớm khoai tây (Early Blight)",
        "symptoms": "Đốm nâu đen có vòng đồng tâm trên lá, làm lá khô héo và rụng.",
        "description": "Do nấm Alternaria solani gây ra, ảnh hưởng lớn đến năng suất củ.",
        "severity": "Trung bình",
        "treatment": {
            "chemical": "Phun Mancozeb, Chlorothalonil hoặc Difenoconazole.",
            "biological": "Sử dụng phân bón sinh học tăng sức đề kháng.",
            "prevention": "Bón phân cân đối, đặc biệt là Kali; vệ sinh đồng ruộng sau thu hoạch."
        }
    },
    "Potato___Late_blight": {
        "disease_name": "Bệnh mốc sương khoai tây (Late Blight)",
        "symptoms": "Vết thâm đen úng nước trên lá và thân, vết bệnh lan nhanh. Củ bị thối màu nâu đỏ.",
        "description": "Do Phytophthora infestans gây ra, là nguyên nhân gây ra nạn đói khoai tây lịch sử.",
        "severity": "Rất cao",
        "treatment": {
            "chemical": "Phun phòng hoặc trị kịp thời bằng Ridomil Gold, Mancozeb, Fosetyl-Aluminium.",
            "biological": "Sử dụng các loại nấm đối kháng bổ sung vào đất.",
            "prevention": "Sử dụng củ giống sạch bệnh, vun luống cao, tiêu hủy tàn dư cây trồng."
        }
    },
    "Pepper,_bell___Bacterial_spot": {
        "disease_name": "Bệnh đốm vi khuẩn hại ớt (Bacterial Spot)",
        "symptoms": "Đốm nhỏ ngậm nước màu xanh vàng trên lá, sau đó chuyển sang nâu đen, lõm ở giữa. Lá bị nhiễm nặng sẽ vàng và rụng. Quả xuất hiện các nốt mụn cóc màu nâu.",
        "description": "Do vi khuẩn Xanthomonas campestris pv. vesicatoria gây ra, lan truyền qua hạt giống, tàn dư cây trồng và nước bắn.",
        "severity": "Cao",
        "treatment": {
            "chemical": "Phun hỗn hợp thuốc gốc đồng với Kasugamycin hoặc Streptomycin.",
            "biological": "Sử dụng chế phẩm sinh học chứa vi khuẩn đối kháng Pseudomonas fluorescens.",
            "prevention": "Sử dụng hạt giống sạch bệnh, xử lý hạt giống bằng nước ấm 50 độ C trong 25 phút, tránh làm việc trong ruộng khi cây còn ướt."
        }
    }
}

class CropHealthAgent:
    def __init__(self):
        self.crop_health_key = os.getenv("CROP_HEALTH_API_KEY", "")
        self.plant_id_key = os.getenv("PLANT_ID_API_KEY", "")
        self.enabled = bool(self.crop_health_key or self.plant_id_key)
        self.demo_fallback = os.getenv("DEMO_FALLBACK", "true").lower() == "true"

    def predict(self, image_path: str, crop_hint: str = "", original_filename: str = "") -> Dict[str, Any]:
        # Handle cases where image doesn't exist
        if not os.path.exists(image_path):
            return {"engine": "crop_health", "enabled": self.enabled, "error": "Image not found", "success": False}

        # Call real APIs if key is available, else return offline status without mock templates
        if self.enabled:
            if self.crop_health_key:
                return self._call_crop_health(image_path)
            elif self.plant_id_key:
                return self._call_plant_id(image_path)
            
        return {
            "engine": "crop_health_offline",
            "success": False,
            "error": "API Key cho Kindwise/Plant.id chưa được cấu hình. Chế độ chẩn đoán đám mây ngoài bị tắt."
        }

    def _call_crop_health(self, image_path: str) -> Dict[str, Any]:
        logger.info("Calling Kindwise crop.health API...")
        try:
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")

            url = "https://api.kindwise.com/v1/crop_health/identification"
            headers = {
                "Api-Key": self.crop_health_key,
                "Content-Type": "application/json"
            }
            payload = {
                "images": [image_b64],
                "details": ["description", "treatment", "symptoms", "severity"]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=25)
            if response.status_code == 200:
                return {
                    "engine": "crop_health_api",
                    "status_code": response.status_code,
                    "data": response.json(),
                    "success": True
                }
            else:
                return {
                    "engine": "crop_health_api",
                    "status_code": response.status_code,
                    "error": response.text,
                    "success": False
                }
        except Exception as exc:
            logger.error(f"Error calling crop.health API: {exc}")
            return {
                "engine": "crop_health_api",
                "error": str(exc),
                "success": False
            }

    def _call_plant_id(self, image_path: str) -> Dict[str, Any]:
        logger.info("Calling Plant.id health API...")
        try:
            with open(image_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")

            url = "https://api.plant.id/v2/health"
            headers = {
                "Api-Key": self.plant_id_key,
                "Content-Type": "application/json"
            }
            payload = {
                "images": [image_b64],
                "modifiers": ["crops_medium"],
                "disease_details": ["description", "treatment", "symptoms"]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=25)
            if response.status_code == 200:
                return {
                    "engine": "plant_id_api",
                    "status_code": response.status_code,
                    "data": response.json(),
                    "success": True
                }
            else:
                return {
                    "engine": "plant_id_api",
                    "status_code": response.status_code,
                    "error": response.text,
                    "success": False
                }
        except Exception as exc:
            logger.error(f"Error calling Plant.id API: {exc}")
            return {
                "engine": "plant_id_api",
                "error": str(exc),
                "success": False
            }

    def _get_mock_response(self, image_path: str, crop_hint: str, original_filename: str = "") -> Dict[str, Any]:
        name_to_check = original_filename if original_filename else os.path.basename(image_path)
        image_name = name_to_check.lower()
        crop = (crop_hint or "tomato").lower()
        
        # Determine disease key
        disease_key = "Tomato___Early_blight"
        if "early_blight" in image_name:
            disease_key = "Potato___Early_blight" if "potato" in image_name or crop == "potato" else "Tomato___Early_blight"
        elif "late_blight" in image_name:
            disease_key = "Potato___Late_blight" if "potato" in image_name or crop == "potato" else "Tomato___Late_blight"
        elif "bacterial_spot" in image_name:
            disease_key = "Pepper,_bell___Bacterial_spot" if "pepper" in image_name or crop == "pepper" else "Tomato___Bacterial_spot"
        else:
            if crop == "potato":
                disease_key = "Potato___Early_blight"
            elif crop == "pepper":
                disease_key = "Pepper,_bell___Bacterial_spot"
            else:
                disease_key = "Tomato___Early_blight"

        details = MOCK_DISEASE_DETAILS.get(disease_key, MOCK_DISEASE_DETAILS["Tomato___Early_blight"])

        return {
            "engine": "crop_health_mock",
            "success": True,
            "api_keys_present": self.enabled,
            "diagnosis": {
                "disease": details["disease_name"],
                "disease_id_key": disease_key,
                "confidence": 0.92,
                "symptoms": details["symptoms"],
                "description": details["description"],
                "severity": details["severity"],
                "treatment": details["treatment"]
            },
            "note": "Mocked Kindwise response for demonstration purposes."
        }
