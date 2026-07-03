import os
import argparse
import torch
from ai_layer.config import settings
from ai_layer.pytorch_engine.model import ImpactTriageNet
from ai_layer.pytorch_engine.inference import get_triage_model

def export_to_onnx(domain: str):
    print(f"\n==========================================")
    print(f"  EXPORTING PYTORCH MODEL TO ONNX - DOMAIN: {domain.upper()}")
    print(f"==========================================\n")
    
    settings.ACTIVE_DOMAIN = domain
    
    model = get_triage_model(domain)
    if not model:
        print("[ONNX Export] PyTorch model checkpoint not found. Please train the model first.")
        return
        
    model.eval()
    
    # Create dummy inputs
    dummy_tab = torch.randn(1, 10, dtype=torch.float32)
    dummy_text = torch.randn(1, 384, dtype=torch.float32)
    
    export_path = os.path.join(settings.domain_dir, "data", "model.onnx")
    
    try:
        import torch.onnx
        
        print(f"[ONNX Export] Exporting model to: {export_path}...")
        torch.onnx.export(
            model,
            (dummy_tab, dummy_text),
            export_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["tab_features", "text_embeddings"],
            output_names=["risk_logits", "priority_score", "review_logits", "confidence_score"],
            dynamic_axes={
                "tab_features": {0: "batch_size"},
                "text_embeddings": {0: "batch_size"},
                "risk_logits": {0: "batch_size"},
                "priority_score": {0: "batch_size"},
                "review_logits": {0: "batch_size"},
                "confidence_score": {0: "batch_size"}
            }
        )
        print(f"[ONNX Export] Successfully exported PyTorch model to ONNX at {export_path}.")
        
        # Verify ONNX model is loadable
        try:
            import onnx
            onnx_model = onnx.load(export_path)
            onnx.checker.check_model(onnx_model)
            print("[ONNX Export] ONNX model structural check passed.")
        except ImportError:
            print("[ONNX Export] Python onnx library not installed. Skipping structural validation check.")
            
    except Exception as e:
        print(f"[ONNX Export] Error during export: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX.")
    parser.add_argument("--domain", type=str, default="sme", choices=["sme", "education", "agriculture"])
    args = parser.parse_args()
    export_to_onnx(args.domain)
