try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    import sys
    class mock_torch:
        class Tensor:
            pass
    sys.modules['torch'] = mock_torch
    import torch
    # Define minimal mock classes to allow importing without PyTorch installed
    class nn:
        class Module:
            def __init__(self, *args, **kwargs):
                pass
        class Linear:
            def __init__(self, *args, **kwargs):
                pass
        class BatchNorm1d:
            def __init__(self, *args, **kwargs):
                pass
        class Dropout:
            def __init__(self, *args, **kwargs):
                pass

class ImpactTriageNet(nn.Module):
    """
    Multi-Task Neural Network in PyTorch for AI-Native Operations Triage.
    Predicts:
    - risk_level (3 classes: Low, Medium, High)
    - priority_score (Regression 0-1)
    - needs_human_review (Binary Classification)
    - confidence (Regression 0-1)
    """
    def __init__(self, tabular_dim: int = 10, text_emb_dim: int = 384, hidden_dim: int = 64):
        super(ImpactTriageNet, self).__init__()
        
        self.input_dim = tabular_dim + text_emb_dim
        
        # Shared representations
        self.shared_layer1 = nn.Linear(self.input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.shared_layer2 = nn.Linear(hidden_dim, hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        
        self.dropout = nn.Dropout(p=0.3)
        
        # Task 1: Risk Level (Multi-class: 3 output units - Low, Med, High)
        self.risk_head = nn.Linear(hidden_dim, 3)
        
        # Task 2: Priority Score (Regression: 1 output unit)
        self.priority_head = nn.Linear(hidden_dim, 1)
        
        # Task 3: Needs Human Review (Binary: 1 output unit)
        self.review_head = nn.Linear(hidden_dim, 1)
        
        # Task 4: Confidence Score (Regression: 1 output unit)
        self.confidence_head = nn.Linear(hidden_dim, 1)

    def forward(self, tab_features: torch.Tensor, text_embs: torch.Tensor):
        # Concatenate inputs
        x = torch.cat((tab_features, text_embs), dim=1)
        
        # Shared layers
        x = F.relu(self.bn1(self.shared_layer1(x)))
        x = self.dropout(x)
        x = F.relu(self.bn2(self.shared_layer2(x)))
        x = self.dropout(x)
        
        # Heads
        risk_logits = self.risk_head(x)
        priority = torch.sigmoid(self.priority_head(x))
        review_logits = self.review_head(x)
        confidence = torch.sigmoid(self.confidence_head(x))
        
        return risk_logits, priority, review_logits, confidence
