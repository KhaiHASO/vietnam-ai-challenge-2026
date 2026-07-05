import re
from typing import Dict, Any

class SymptomAgent:
    def parse_symptoms(self, symptoms_text: str) -> Dict[str, Any]:
        if not symptoms_text:
            return {
                "rain_after": "unknown",
                "fruit_spots": False,
                "spread_speed": "unknown",
                "raw_text": ""
            }
            
        text = symptoms_text.lower()
        
        # Extract rain_after duration
        rain_after = "none"
        if "mưa" in text or "rain" in text:
            match = re.search(r"(\d+)\s*ngày", text)
            if match:
                rain_after = f"{match.group(1)} days"
            else:
                rain_after = "3 days"
                
        # Extract fruit_spots boolean
        fruit_spots = any(k in text for k in ["quả", "trái", "fruit", "spot on fruit"])
        
        # Extract spread_speed
        spread_speed = "medium"
        if any(k in text for k in ["nhanh", "fast", "rapid", "lan rộng"]):
            spread_speed = "high"
        elif any(k in text for k in ["chậm", "slow", "từ từ"]):
            spread_speed = "slow"
            
        return {
            "rain_after": rain_after,
            "fruit_spots": fruit_spots,
            "spread_speed": spread_speed,
            "raw_text": symptoms_text
        }
