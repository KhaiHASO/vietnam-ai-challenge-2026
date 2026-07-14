import os
import argparse
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from ai_layer.config import settings
from ai_layer.pytorch_engine.model import ImpactTriageNet
from ai_layer.pytorch_engine.dataset import OperationsTriageDataset

def train_model(domain: str, epochs: int = 15, batch_size: int = 16, lr: float = 0.001):
    print(f"\n==========================================")
    print(f"  TRAINING PYTORCH MODEL - DOMAIN: {domain.upper()}")
    print(f"==========================================\n")
    
    # 1. Initialize the request-scoped domain dataset.
    dataset = OperationsTriageDataset(domain=domain, num_samples=300)
    
    # 3. Train-Val Split
    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 4. Instantiate Model
    model = ImpactTriageNet(tabular_dim=10, text_emb_dim=384, hidden_dim=64)
    
    # 5. Loss Heads
    criterion_risk = nn.CrossEntropyLoss()
    criterion_priority = nn.MSELoss()
    criterion_review = nn.BCEWithLogitsLoss()
    criterion_confidence = nn.MSELoss()
    
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    # Checkpoint Path
    checkpoint_dir = settings.data_path(domain)
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, "model_checkpoint.pth")
    
    best_val_loss = float("inf")
    history = {"train_loss": [], "val_loss": [], "val_risk_acc": []}
    
    # 6. Training Loop
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        
        for batch in train_loader:
            tab_feats = batch["tab_features"]
            text_embs = batch["text_emb"]
            
            risk_labels = batch["risk_label"]
            priority_targets = batch["priority_score"].unsqueeze(1)
            review_targets = batch["needs_review"].unsqueeze(1)
            confidence_targets = batch["confidence_score"].unsqueeze(1)
            
            # Forward pass
            risk_logits, priority_preds, review_logits, confidence_preds = model(tab_feats, text_embs)
            
            # Compute Multi-Task Losses
            loss_risk = criterion_risk(risk_logits, risk_labels)
            loss_priority = criterion_priority(priority_preds, priority_targets)
            loss_review = criterion_review(review_logits, review_targets)
            loss_confidence = criterion_confidence(confidence_preds, confidence_targets)
            
            # Weighted loss sum
            loss = 1.0 * loss_risk + 2.0 * loss_priority + 1.0 * loss_review + 1.0 * loss_confidence
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * tab_feats.size(0)
            
        epoch_loss /= len(train_loader.dataset)
        
        # Validation Pass
        model.eval()
        val_loss = 0.0
        correct_risk = 0
        total_risk = 0
        
        with torch.no_grad():
            for batch in val_loader:
                tab_feats = batch["tab_features"]
                text_embs = batch["text_emb"]
                
                risk_labels = batch["risk_label"]
                priority_targets = batch["priority_score"].unsqueeze(1)
                review_targets = batch["needs_review"].unsqueeze(1)
                confidence_targets = batch["confidence_score"].unsqueeze(1)
                
                risk_logits, priority_preds, review_logits, confidence_preds = model(tab_feats, text_embs)
                
                loss_risk = criterion_risk(risk_logits, risk_labels)
                loss_priority = criterion_priority(priority_preds, priority_targets)
                loss_review = criterion_review(review_logits, review_targets)
                loss_confidence = criterion_confidence(confidence_preds, confidence_targets)
                
                loss = 1.0 * loss_risk + 2.0 * loss_priority + 1.0 * loss_review + 1.0 * loss_confidence
                val_loss += loss.item() * tab_feats.size(0)
                
                # Check accuracy of risk classification
                risk_preds = torch.argmax(risk_logits, dim=1)
                correct_risk += (risk_preds == risk_labels).sum().item()
                total_risk += risk_labels.size(0)
                
        val_loss /= len(val_loader.dataset)
        risk_acc = correct_risk / total_risk if total_risk > 0 else 0
        
        history["train_loss"].append(epoch_loss)
        history["val_loss"].append(val_loss)
        history["val_risk_acc"].append(risk_acc)
        
        print(f"Epoch {epoch+1:02d}/{epochs:02d} | Train Loss: {epoch_loss:.4f} | Val Loss: {val_loss:.4f} | Risk Acc: {risk_acc*100:.2f}%")
        
        # Save Best Model Checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "domain": domain
            }, checkpoint_path)
            
    print(f"\n[PyTorch Engine] Model training completed. Best validation loss: {best_val_loss:.4f}")
    print(f"[PyTorch Engine] Saved checkpoint to: {checkpoint_path}")
    
    # Save training history summary JSON
    history_path = os.path.join(checkpoint_dir, "train_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
        
    return checkpoint_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train multi-task operations triage model.")
    parser.add_argument("--domain", type=str, default="sme", choices=["sme", "education", "agriculture"], help="Target domain config")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    args = parser.parse_args()
    
    train_model(args.domain, args.epochs, args.batch_size)
