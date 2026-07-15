# Model Card: PyTorch Operations Triage Net (ImpactTriageNet)

This model card details the specifications, design decisions, performance, and validation status of the PyTorch Multi-Task Operations Triage neural network integrated in the CropDoctor AI Platform.

## Model Details
- **Developer**: FPT Polytechnic Đồng Nai - Team Khải
- **Architecture**: `ImpactTriageNet` - Multi-task Feed-Forward Neural Network in PyTorch with tabular and text embedding fusion.
- **Tasks**:
  1. **Risk Triage (`risk_level`)**: Multi-class classification (Low, Medium, High).
  2. **Priority Prediction (`priority_score`)**: Regression value between 0.0 and 1.0.
  3. **Needs Human Approval (`needs_human_review`)**: Binary classification (requires expert review / trigger HITL).
  4. **Confidence Scoring (`confidence_score`)**: Regression value between 0.0 and 1.0 representing model certainty.
- **Language**: Python (PyTorch 2.0+)
- **Version**: 1.0

## Intended Use
- **Primary Use Case**: Automatically classify incoming agricultural disease cases, prioritize them based on damage metrics and environmental urgency, flag actions with chemical/IPM risk for expert verification, and compute model confidence.
- **Flexible Domain Packaging**: Configured dynamically for agricultural crop diseases.

## Training Data & Features
The model accepts two inputs:
1. **Tabular Features (10 dimensions)**:
   - *Agriculture Domain*: Leaf damage percentages, temperature, humidity, soil moisture, days since last treatment.
2. **Text Embeddings (384 dimensions)**: Generated using a lightweight SentenceTransformer (`all-MiniLM-L6-v2`) on query text / description.

## Metrics (Synthetic Evaluation)
- **Risk Level Accuracy**: ~90-95%
- **Review Requirement F1 Score**: ~92%
- **Priority Mean Squared Error (MSE)**: < 0.01

## Performance and Latency
- **Inference Speed**: Under 1.5ms on modern CPU, under 0.5ms with `torch.compile` optimization.
- **Throughput**: > 600 predictions/sec on CPU.
- **Deployment**: Supports ONNX runtime export (`model.onnx`) for microservice integration.

## Ethical Considerations & Human Oversight
- **Human-in-the-Loop constraint**: The model does NOT execute high-risk actions. High-risk intents trigger a pending approval ticket in the expert dashboard (`HITL Queue`) regardless of raw prediction.
- **Confidence Thresholding**: Predictions with low confidence fall back to asking the user clarifying questions.
