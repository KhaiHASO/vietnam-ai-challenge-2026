# PyTorch Award Strategy: Impact Triage Engine

Tài liệu này trình bày chi tiết kiến trúc và chiến lược kỹ thuật sử dụng mô hình PyTorch trong giải pháp **AI-Native Operations Copilot** để tranh giải **Best PyTorch Award**.

## 1. Why PyTorch? (Tại sao cần PyTorch mà không dùng LLM hết?)
- **Hiệu năng & Chi phí**: LLM hoạt động xuất sắc trong việc hiểu ngôn ngữ tự nhiên và lập kế hoạch (planning), nhưng cực kỳ đắt đỏ và có độ trễ lớn (2-5 giây) khi phân loại hoặc đưa ra các điểm số rủi ro nghiệp vụ liên tục.
- **Tính chính xác & Khả năng kiểm toán (Auditability)**: Các mô hình học sâu chuyên biệt được train trên tập dữ liệu hẹp chạy nhanh (< 2ms trên CPU), cho ra kết quả dự đoán định lượng phân phối xác suất rõ ràng và có thể kiểm chứng bằng toán học (F1-score, Precision, Recall).
- **Phối hợp đa nhiệm (Multi-tasking)**: Mô hình PyTorch `ImpactTriageNet` của chúng em giải quyết đồng thời 4 nhiệm vụ vận hành chỉ với một lượt forward duy nhất.

## 2. Kiến trúc Mô hình (Model Architecture)
Mô hình được viết kế thừa lớp `torch.nn.Module` trong tệp `ai_layer/pytorch_engine/model.py`:
- **Đầu vào**:
  - `tab_features` ($1 \times 10$): Tập hợp các chỉ số định lượng của hệ thống (ví dụ: giá trị đơn hàng, tỷ lệ chuyên cần, phần trăm thiệt hại lá).
  - `text_embeddings` ($1 \times 384$): Feature vector được trích xuất từ tin nhắn/yêu cầu bằng SentenceTransformer.
- **Lớp mạng chung (Shared Layers)**:
  - Linear layer kết hợp Batch Normalization, Activation ReLU và Dropout (rate=0.3) nhằm hạn chế Overfitting.
- **Các đầu ra chuyên biệt (Multi-Task Heads)**:
  - **Risk Head** (`nn.Linear(hidden, 3)`): Đánh giá 3 lớp rủi ro (Low, Medium, High). Loss function: CrossEntropyLoss.
  - **Priority Head** (`nn.Linear(hidden, 1)` -> Sigmoid): Đánh giá mức độ khẩn cấp (0 đến 1). Loss function: MSELoss.
  - **Review Head** (`nn.Linear(hidden, 1)` -> Logits): Dự đoán có cần kích hoạt duyệt HITL hay không. Loss function: BCEWithLogitsLoss.
  - **Confidence Head** (`nn.Linear(hidden, 1)` -> Sigmoid): Ước lượng độ tin cậy của mô hình (0 đến 1). Loss function: MSELoss.

```text
Input Features (Tabular + Text Embeddings)
         │
         ▼
Shared Dense Layer 1 (ReLU + BatchNorm + Dropout)
         │
         ▼
Shared Dense Layer 2 (ReLU + BatchNorm + Dropout)
         ├───► Risk Head (CrossEntropy Loss) -> risk_level (Low/Med/High)
         ├───► Priority Head (MSE Loss) -> priority_score (0-1)
         ├───► Review Head (BCE Loss) -> needs_human_review (bool)
         └───► Confidence Head (MSE Loss) -> confidence_score (0-1)
```

## 3. Chiến lược Tối ưu hóa (Optimization & Deployment)
- **Tối ưu hóa biên dịch**: Sử dụng `torch.compile` (nếu môi trường Windows hỗ trợ PyTorch 2.0+) cho việc tăng tốc độ suy luận (inference speedup lên tới 30%).
- **Xuất ONNX**: Module `export_onnx.py` xuất mô hình sang ONNX runtime (`model.onnx`) để chạy suy luận không phụ thuộc vào thư viện PyTorch gốc trên các thiết bị Edge/Mobile.
- **Trình bày Benchmark**: Tệp `results/latency_benchmark.json` lưu giữ báo cáo hiệu năng đo đạc qua 100 lần chạy liên tiếp để chứng minh mức độ sẵn sàng triển khai thực tế.
