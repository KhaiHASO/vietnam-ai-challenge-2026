# Risk and Mitigation Plan - Student Success Copilot

Các rủi ro về mặt công nghệ, đạo đức giáo dục và bảo mật thông tin khi ứng dụng AI vào học đường.

## 1. Rủi ro Định kiến và Thiên lệch (Bias Risk)
- **Mô tả**: Mô hình PyTorch đánh giá sai lệch rủi ro học tập của một nhóm sinh viên cụ thể do dữ liệu huấn luyện lịch sử không cân bằng (ví dụ: thiên vị sinh viên ngành công nghệ hơn kinh tế).
- **Biện pháp khắc phục**:
  - Thực hiện cân bằng dữ liệu (oversampling/undersampling) khi huấn luyện mô hình PyTorch.
  - Sử dụng tham số `confidence_score` được dự đoán trực tiếp từ mô hình. Nếu độ tin cậy thấp, hệ thống tự động ẩn đề xuất và yêu cầu CVHT tự đánh giá thủ công.

## 2. Rủi ro Bảo mật Thông tin Học tập (FERPA / PII Compliance)
- **Mô tả**: Dữ liệu điểm số và thông tin cá nhân của sinh viên bị rò rỉ khi truyền nhận dữ liệu với các API LLM thương mại bên ngoài.
- **Biện pháp khắc phục**:
  - Kích hoạt **PIIScanner** mã hóa toàn bộ Tên sinh viên, MSSV thành các chuỗi ngẫu nhiên trước khi đưa vào prompt của LLM.
  - Sử dụng các LLM nguồn mở chạy cục bộ (như Llama 3.2 qua Ollama) trên hạ tầng máy chủ của nhà trường để xử lý dữ liệu nhạy cảm học tập.

## 3. Rủi ro Áp lực Tâm lý (Psychological Impact)
- **Mô tả**: Sinh viên nhận được cảnh báo tự động quá dồn dập hoặc lời lẽ gay gắt dẫn đến chán nản, bỏ học.
- **Biện pháp khắc phục**:
  - RAG được nạp các prompt mẫu hướng dẫn viết tin nhắn theo văn phong động viên, xây dựng, tránh trừng phạt.
  - Khóa tính năng tự động gửi tin nhắn. Bắt buộc CVHT phải đọc, hiệu chỉnh và ký duyệt thủ công (HITL) cho mọi tin nhắn cảnh báo học vụ chính thức.
