# Problem Brief: SME Operations Copilot

## 1. Context (Bối cảnh)
Các doanh nghiệp vừa và nhỏ (SMEs) cung cấp dịch vụ (như trung tâm thể thao, cho thuê sân bãi, phòng gym) thường gặp khó khăn lớn trong việc đồng bộ hóa dữ liệu vận hành. Thông tin đơn đặt chỗ (booking), phản hồi khách hàng (inbox/Zalo), sự cố kỹ thuật và các giao dịch tài chính bị lỗi thường nằm rải rác ở nhiều kênh khác nhau.

## 2. Problem Statement (Bài toán đặt ra)
- **Quá tải thông tin**: Chủ doanh nghiệp hoặc nhân viên trực quầy bị ngập trong hàng trăm tin nhắn khiếu nại, báo lỗi thanh toán mà không có công cụ phân loại mức độ khẩn cấp (priority) và rủi ro (risk).
- **Trì trệ trong xử lý**: Việc tra cứu thủ công chính sách hoàn tiền, hủy sân mất nhiều thời gian, dẫn đến bỏ sót khiếu nại của khách hàng VIP hoặc khách có sự cố tài chính lớn.
- **Rủi ro thất thoát**: Cho phép nhân viên tự động thực hiện các thao tác hoàn tiền hoặc sửa đổi đặt chỗ mà không có sự kiểm duyệt của quản lý dễ dẫn đến gian lận.

## 3. Targeted Solution (Giải pháp đề xuất)
Xây dựng một **AI-Native Operations Copilot** đóng vai trò là một "Cockpit hành động" trung tâm:
1. **Phân loại tự động (PyTorch Engine)**: Nhận biết mức độ rủi ro nghiệp vụ và chấm điểm ưu tiên cho các yêu cầu từ khách hàng.
2. **Hỗ trợ dựa trên dữ liệu (RAG)**: Truy xuất nhanh chóng các điều khoản và chính sách hoàn hủy sân để đưa ra khuyến nghị chuẩn xác.
3. **Kiểm soát giao dịch (HITL)**: Tự động chặn các yêu cầu hủy/hoàn tiền và đưa vào hàng đợi duyệt của Admin (HITL Queue).
4. **Vận hành khép kín (Tool Call)**: Tạo nhanh ticket kỹ thuật hoặc cập nhật cơ sở dữ liệu sau khi được phê duyệt.
