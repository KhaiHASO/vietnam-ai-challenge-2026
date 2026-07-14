import os
import argparse
import json
import torch
from torch.utils.data import DataLoader
from ai_layer.config import settings
from ai_layer.pytorch_engine.model import ImpactTriageNet
from ai_layer.pytorch_engine.dataset import OperationsTriageDataset

def evaluate_model(domain: str):
    print(f"\n==========================================")
    print(f"  EVALUATING PYTORCH MODEL - DOMAIN: {domain.upper()}")
    print(f"==========================================\n")
    
    checkpoint_path = settings.data_path(domain) / "model_checkpoint.pth"
    
    if not os.path.exists(checkpoint_path):
        print(f"[PyTorch Eval] Checkpoint not found at {checkpoint_path}. Train the model first.")
        return
        
    # Load dataset
    dataset = OperationsTriageDataset(domain=domain, num_samples=100)
    eval_loader = DataLoader(dataset, batch_size=8, shuffle=False)
    
    # Load model
    model = ImpactTriageNet(tabular_dim=10, text_emb_dim=384, hidden_dim=64)
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    # Eval collections
    all_risk_preds = []
    all_risk_labels = []
    
    all_priority_preds = []
    all_priority_targets = []
    
    all_review_preds = []
    all_review_targets = []
    
    all_confidence_preds = []
    all_confidence_targets = []
    
    with torch.no_grad():
        for batch in eval_loader:
            tab_feats = batch["tab_features"]
            text_embs = batch["text_emb"]
            
            risk_labels = batch["risk_label"]
            priority_targets = batch["priority_score"]
            review_targets = batch["needs_review"]
            confidence_targets = batch["confidence_score"]
            
            risk_logits, priority_preds, review_logits, confidence_preds = model(tab_feats, text_embs)
            
            # Risk preds
            risk_preds = torch.argmax(risk_logits, dim=1)
            all_risk_preds.extend(risk_preds.numpy().tolist())
            all_risk_labels.extend(risk_labels.numpy().tolist())
            
            # Priority
            all_priority_preds.extend(priority_preds.squeeze(1).numpy().tolist())
            all_priority_targets.extend(priority_targets.numpy().tolist())
            
            # Review (BCE logits review prediction threshold at 0.0)
            review_preds = (review_logits.squeeze(1) >= 0.0).float()
            all_review_preds.extend(review_preds.numpy().tolist())
            all_review_targets.extend(review_targets.numpy().tolist())
            
            # Confidence
            all_confidence_preds.extend(confidence_preds.squeeze(1).numpy().tolist())
            all_confidence_targets.extend(confidence_targets.numpy().tolist())

    # Manual compute metrics to guarantee zero external dependency crash
    # 1. Risk accuracy
    correct_risk = sum(1 for p, l in zip(all_risk_preds, all_risk_labels) if p == l)
    risk_acc = correct_risk / len(all_risk_labels) if all_risk_labels else 0
    
    # 2. Priority MSE
    priority_mse = sum((p - t)**2 for p, t in zip(all_priority_preds, all_priority_targets)) / len(all_priority_targets)
    
    # 3. Needs Review Accuracy/Recall/F1
    tp = sum(1 for p, t in zip(all_review_preds, all_review_targets) if p == 1 and t == 1)
    fp = sum(1 for p, t in zip(all_review_preds, all_review_targets) if p == 1 and t == 0)
    fn = sum(1 for p, t in zip(all_review_preds, all_review_targets) if p == 0 and t == 1)
    tn = sum(1 for p, t in zip(all_review_preds, all_review_targets) if p == 0 and t == 0)
    
    review_acc = (tp + tn) / len(all_review_targets) if all_review_targets else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    review_f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = {
        "domain": domain,
        "eval_samples": len(all_risk_labels),
        "risk_classification_accuracy": round(risk_acc, 4),
        "priority_regression_mse": round(priority_mse, 6),
        "review_classification_accuracy": round(review_acc, 4),
        "review_precision": round(precision, 4),
        "review_recall": round(recall, 4),
        "review_f1": round(review_f1, 4),
        "avg_predicted_confidence": round(sum(all_confidence_preds)/len(all_confidence_preds), 4)
    }
    
    print("------------------------------------------")
    print(f"Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  - {k}: {v}")
    print("------------------------------------------")
    
    # Save metrics.json
    metrics_path = settings.data_path(domain) / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[PyTorch Eval] Saved evaluation metrics to: {metrics_path}")
    
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate triage model.")
    parser.add_argument("--domain", type=str, default="sme", choices=["sme", "education", "agriculture"])
    args = parser.parse_args()
    evaluate_model(args.domain)
