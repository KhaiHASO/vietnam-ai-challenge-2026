# Pilot Pathway: SME Operations Copilot

Tài liệu này vạch ra lộ trình thử nghiệm thực tế (pilot) của giải pháp **SME Operations Copilot** tại một trung tâm thể thao mẫu trong thời gian 2 tuần.

## 1. Phase 1: Preparation & Offline Evaluation (Ngày 1 - 3)
- **Mục tiêu**: Thu thập 200 mẫu log lịch sử chat khiếu nại và giao dịch để làm dữ liệu kiểm thử.
- **Hành động**: 
  - Khởi tạo RAG với chính sách hủy/hoàn tiền gốc của sân.
  - Huấn luyện mô hình PyTorch Risk Engine trên dữ liệu giả lập có bổ sung nhiễu.
- **Tiêu chí đạt**: Độ chính xác của mô hình PyTorch trong việc phát hiện các giao dịch rủi ro cao đạt trên **90%**.

## 2. Phase 2: Shadow Mode (Ngày 4 - 7)
- **Mục tiêu**: Đánh giá hiệu năng của AI trong môi trường thực tế mà không ảnh hưởng đến khách hàng.
- **Hành động**: 
  - Hệ thống AI chạy song song ở chế độ "Shadow" (bóng tối). Khi có tin nhắn đến, AI sẽ tự động phân loại, tra cứu chính sách và đề xuất hành động.
  - Nhân viên vận hành vẫn xử lý thủ công theo quy trình cũ.
  - Cuối ngày, so sánh kết quả xử lý của nhân viên và đề xuất của AI.
- **Tiêu chí đạt**: Không có trường hợp nào AI bỏ sót giao dịch rủi ro cao (Zero False Negatives cho rủi ro High).

## 3. Phase 3: Limited Pilot (Ngày 8 - 14)
- **Mục tiêu**: Chuyển giao quyền xử lý bước đầu cho AI dưới sự kiểm soát chặt chẽ của con người.
- **Hành động**:
  - Tích hợp giao diện AI Cockpit vào quầy lễ tân của 1 chi nhánh sân Pickleball.
  - Cho phép AI tự động trả lời các câu hỏi FAQ thường gặp.
  - Các yêu cầu hủy/hoàn tiền được AI tạo ticket tự động và đẩy vào danh sách phê duyệt của Quản lý chi nhánh.
- **Tiêu chí đạt**:
  - Thời gian xử lý trung bình giảm từ **12 phút xuống dưới 2 phút**.
  - Nhân viên hài lòng với các đề xuất phản hồi của AI (tỷ lệ chấp nhận đề xuất > 80%).

## 4. Phase 4: Full Deployment & Scaling (Sau tuần 2)
- Mở rộng ra toàn bộ hệ thống các chi nhánh sân thể thao.
- Tích hợp thêm các kênh tự động hoàn tiền trực tiếp qua API ví điện tử (chỉ kích hoạt sau khi có chữ ký số phê duyệt của Admin).
