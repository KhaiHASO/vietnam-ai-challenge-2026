# Risk and Mitigation Plan - SME Operations Copilot

Tài liệu này xác định các rủi ro kỹ thuật, nghiệp vụ khi đưa AI vào quy trình vận hành dịch vụ khách hàng và cách khắc phục.

## 1. Rủi ro Ảo tưởng (Hallucination Risk)
- **Mô tả**: LLM tự tạo ra các chính sách hoàn tiền không tồn tại (ví dụ: hứa hoàn tiền 100% dù khách hủy sát giờ) gây thiệt hại tài chính.
- **Biện pháp khắc phục**:
  - Dùng **Output Guardrail Check** đo lường độ trùng khớp ngữ nghĩa (Cosine Similarity) giữa câu trả lời của LLM với văn bản chính sách được truy xuất từ Vector DB.
  - Thiết lập ngưỡng cảnh báo (Threshold = 0.5). Nếu câu trả lời có độ tương đồng thấp, hệ thống tự động chặn phản hồi và chuyển sang chế độ fallback an toàn.

## 2. Rủi ro An toàn Thông tin (PII Data Leakage)
- **Mô tả**: Gửi thông tin nhạy cảm của khách hàng (như số điện thoại, số tài khoản ví MoMo) lên API LLM đám mây vi phạm chính sách bảo mật dữ liệu cá nhân.
- **Biện pháp khắc phục**:
  - Tích hợp module **PIIScanner** quét đầu vào bằng biểu thức chính quy (Regex) và Named Entity Recognition (NER).
  - Thay thế số điện thoại thành `[PHONE_REDACTED]` và số tài khoản thành `[ACCOUNT_REDACTED]` trước khi gửi lên LLM.
  - Ánh xạ ngược lại (Restore) thông tin thật ở đầu ra cục bộ trên máy chủ backend trước khi hiển thị lên giao diện người dùng.

## 3. Rủi ro Gian lận Giao dịch (Financial Fraud)
- **Mô tả**: Kẻ tấn công lợi dụng lỗ hổng Prompt Injection để ép AI tự động thực hiện lệnh hoàn tiền mà không có giao dịch thật.
- **Biện pháp khắc phục**:
  - Mô hình PyTorch Impact Triage Engine hoạt động độc lập với LLM để phân loại tính chất giao dịch.
  - **Human-in-the-loop (HITL)**: Khóa cứng tính năng hoàn tiền tự động qua API. Bất kỳ giao dịch hoàn tiền nào cũng bắt buộc phải có lệnh phê duyệt (Approve) từ Quản trị viên thông qua chữ ký số hoặc nút bấm bảo mật trên admin dashboard.
  - Lưu trữ nhật ký kiểm toán (Audit logs) chi tiết cho mọi hành động phê duyệt để phục vụ hậu kiểm.
