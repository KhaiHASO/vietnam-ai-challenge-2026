import os
import json
import numpy as np
from ai_layer.config import settings
from ai_layer.pytorch_engine.model import ImpactTriageNet
from ai_layer.rag.vector_db import LocalVectorDB

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# Keep model instance in-memory cache to save startup latency
_MODEL_CACHE = {}

def get_triage_model(domain: str):
    """Loads and caches the model for the active domain."""
    global _MODEL_CACHE
    if not HAS_TORCH:
        return None
    
    checkpoint_path = os.path.join(settings.domain_dir, "data", "model_checkpoint.pth")
    
    if not os.path.exists(checkpoint_path):
        print(f"[PyTorch Inference] Checkpoint not found at {checkpoint_path}. Running fast auto-train...")
        # Auto-train with few epochs if not found
        try:
            from ai_layer.pytorch_engine.train import train_model
            train_model(domain, epochs=3, batch_size=8)
        except Exception as e:
            print(f"[PyTorch Inference] Auto-training failed: {e}. Falling back to rule-based triage.")
            return None
            
    if not os.path.exists(checkpoint_path):
        return None
        
    cache_key = f"{domain}_{os.path.getmtime(checkpoint_path)}"
    
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]
        
    try:
        model = ImpactTriageNet(tabular_dim=10, text_emb_dim=384, hidden_dim=64)
        checkpoint = torch.load(checkpoint_path, map_location=torch.device("cpu"))
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        _MODEL_CACHE[cache_key] = model
        print(f"[PyTorch Inference] Loaded model checkpoint for domain '{domain}' successfully.")
        return model
    except Exception as e:
        print(f"[PyTorch Inference] Error loading model: {e}")
        return None

def predict_triage(description: str, metadata: dict) -> dict:
    """
    Predicts triage risk, priority, review requirement, and confidence using the PyTorch engine.
    """
    domain = settings.ACTIVE_DOMAIN
    if not HAS_TORCH:
        return run_rule_based_fallback(domain, description, metadata)
        
    model = get_triage_model(domain)
    
    # 1. Fallback Rule-Based Engine (if PyTorch fails or model not trained)
    if not model:
        return run_rule_based_fallback(domain, description, metadata)
        
    try:
        vector_db = LocalVectorDB()
        
        # 2. Extract Tabular Features (10 dims)
        tab_features = np.zeros((1, 10), dtype=np.float32)
        top_factors = []
        
        if domain == "sme":
            order_value = float(metadata.get("order_value", 0.0))
            loyalty = float(metadata.get("customer_loyalty_tier", 2.0))
            pending = float(metadata.get("pending_tickets_count", 0.0))
            is_fin = float(metadata.get("is_financial_transaction", 0.0))
            
            tab_features[0, 0] = order_value / 1000000.0
            tab_features[0, 1] = loyalty / 5.0
            tab_features[0, 2] = pending / 10.0
            tab_features[0, 3] = is_fin
            
            if order_value > 500000:
                top_factors.append("order_value_above_threshold")
            if is_fin > 0:
                top_factors.append("financial_transaction_risk")
            if pending > 2:
                top_factors.append("multiple_pending_tickets")
                
        elif domain == "education":
            gpa = float(metadata.get("prior_gpa", 3.0))
            attendance = float(metadata.get("attendance_rate", 0.95))
            late = float(metadata.get("late_submissions_count", 0.0))
            lms = float(metadata.get("lms_activity_score", 80.0))
            midterm = float(metadata.get("midterm_grade", 8.0))
            
            tab_features[0, 0] = gpa / 4.0
            tab_features[0, 1] = attendance
            tab_features[0, 2] = late / 10.0
            tab_features[0, 3] = lms / 100.0
            tab_features[0, 4] = midterm / 10.0
            
            if attendance < 0.8:
                top_factors.append("low_attendance_warning")
            if midterm < 5.0:
                top_factors.append("failing_midterm_grade")
            if late > 3:
                top_factors.append("multiple_late_assignments")
                
        elif domain == "agriculture":
            damage = float(metadata.get("leaf_damage_percent", 0.0))
            temp = float(metadata.get("temperature", 28.0))
            hum = float(metadata.get("humidity", 70.0))
            soil = float(metadata.get("soil_moisture", 60.0))
            days_since = float(metadata.get("days_since_last_treatment", 0.0))
            
            tab_features[0, 0] = damage / 100.0
            tab_features[0, 1] = (temp - 15.0) / 30.0
            tab_features[0, 2] = hum / 100.0
            tab_features[0, 3] = soil / 100.0
            tab_features[0, 4] = days_since / 30.0
            
            if damage > 20.0:
                top_factors.append("significant_crop_damage")
            if soil < 40.0:
                top_factors.append("soil_moisture_depleted")
            if days_since > 15.0:
                top_factors.append("extended_period_without_treatment")
                
        # Fill noise/pad
        np.random.seed(42)
        tab_features += np.random.normal(0, 0.02, (1, 10))
        
        # 3. Extract Text Embedding (384 dims)
        text_emb = vector_db.get_embedding(description).reshape(1, 384)
        
        # 4. Perform Inference
        tab_tensor = torch.tensor(tab_features, dtype=torch.float32)
        text_tensor = torch.tensor(text_emb, dtype=torch.float32)
        
        with torch.no_grad():
            risk_logits, priority_preds, review_logits, confidence_preds = model(tab_tensor, text_tensor)
            
        risk_class = int(torch.argmax(risk_logits, dim=1).item())
        risk_map = {0: "low", 1: "medium", 2: "high"}
        risk_level = risk_map.get(risk_class, "low")
        
        priority = float(priority_preds.item())
        needs_review = bool(review_logits.item() >= 0.0)
        confidence = float(confidence_preds.item())
        
        return {
            "risk_level": risk_level,
            "priority": round(priority, 4),
            "needs_human_review": needs_review,
            "confidence": round(confidence, 4),
            "top_factors": top_factors or ["general_query_profile"],
            "model_version": "impact-triage-v1.0",
            "engine": "PyTorch Neural Network"
        }
        
    except Exception as e:
        print(f"[PyTorch Inference] Exception during model forward pass: {e}. Falling back...")
        return run_rule_based_fallback(domain, description, metadata)

def run_rule_based_fallback(domain: str, description: str, metadata: dict) -> dict:
    """Heuristic logic fallback when PyTorch weights are loading/missing."""
    desc_lower = description.lower()
    top_factors = []
    
    if domain == "sme":
        order_value = float(metadata.get("order_value", 0.0))
        is_fin = bool(metadata.get("is_financial_transaction", False))
        
        # Simple heuristic
        if order_value >= 500000 or "hoàn tiền" in desc_lower or "momo" in desc_lower:
            risk = "high"
            priority = 0.85
            review = True
            top_factors.append("financial_transaction_threshold")
        elif "hủy" in desc_lower or order_value > 200000:
            risk = "medium"
            priority = 0.65
            review = True
            top_factors.append("cancellation_or_medium_value")
        else:
            risk = "low"
            priority = 0.25
            review = False
            top_factors.append("general_faq_profile")
            
    elif domain == "education":
        attendance = float(metadata.get("attendance_rate", 0.95))
        midterm = float(metadata.get("midterm_grade", 8.0))
        
        if attendance < 0.75 or midterm < 5.0 or "vắng" in desc_lower:
            risk = "high"
            priority = 0.90
            review = True
            top_factors.append("academic_risk_alert")
        elif attendance < 0.85 or "muộn" in desc_lower:
            risk = "medium"
            priority = 0.55
            review = True
            top_factors.append("attendance_slipping")
        else:
            risk = "low"
            priority = 0.15
            review = False
            top_factors.append("normal_student_profile")
            
    elif domain == "agriculture":
        damage = float(metadata.get("leaf_damage_percent", 0.0))
        
        if damage > 40.0 or "sâu bệnh" in desc_lower or "hạn" in desc_lower:
            risk = "high"
            priority = 0.95
            review = True
            top_factors.append("severe_crop_pest_damage")
        elif damage > 15.0 or "lá vàng" in desc_lower:
            risk = "medium"
            priority = 0.60
            review = True
            top_factors.append("moderate_crop_stress")
        else:
            risk = "low"
            priority = 0.30
            review = False
            top_factors.append("healthy_crop_profile")
            
    return {
        "risk_level": risk,
        "priority": priority,
        "needs_human_review": review,
        "confidence": 0.99,
        "top_factors": top_factors,
        "model_version": "fallback-heuristics-v1.0",
        "engine": "Rule-Based Fallback"
    }
