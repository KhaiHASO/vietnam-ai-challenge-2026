from typing import Dict, Any

class ContextAgent:
    def get_context(self, location: str) -> Dict[str, Any]:
        loc_lower = location.lower() if location else ""
        
        # Determine environmental context based on location
        if "trảng bom" in loc_lower or "trang bom" in loc_lower or "ot" in loc_lower:
            return {
                "humidity": "89%",
                "rainfall": "42mm",
                "spray_gap": "7d",
                "location": "Trảng Bom"
            }
        elif "long thành" in loc_lower or "long thanh" in loc_lower or "ca" in loc_lower:
            return {
                "humidity": "78%",
                "rainfall": "15mm",
                "spray_gap": "14d",
                "location": "Long Thành"
            }
        else:
            return {
                "humidity": "82%",
                "rainfall": "25mm",
                "spray_gap": "10d",
                "location": location or "Đồng Nai"
            }
