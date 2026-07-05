from typing import Dict, Any

class SafetyAgent:
    def verify_safety(self, disease_label: str, confidence: float) -> Dict[str, Any]:
        # Emphasize IPM methods first
        ipm_first = True
        
        # Determine if expert intervention is needed
        # Severe diseases like Late Blight or low confidence calls require experts
        disease_lower = disease_label.lower() if disease_label else ""
        expert_needed = confidence < 0.60 or "late_blight" in disease_lower or "fusarium" in disease_lower
        
        # Chemical advice policy
        chemical_advice = "deferred"
        if confidence >= 0.85 and not expert_needed:
            chemical_advice = "recommended"
            
        return {
            "ipm_first": ipm_first,
            "chemical_advice": chemical_advice,
            "expert_needed": expert_needed
        }
