# Problem Brief: Student Success Copilot (Education Domain)

## 1. Context (Bối cảnh)
Trong các trường đại học và cơ sở giáo dục, cố vấn học tập (CVHT) và giảng viên phải quản lý số lượng sinh viên rất lớn (lên tới hàng trăm sinh viên mỗi người). Dữ liệu học tập như điểm số, tỷ lệ vắng mặt trên lớp, hoạt động trên hệ thống LMS và bài nộp muộn nằm phân tán ở các phần mềm quản lý khác nhau.

## 2. Problem Statement (Bài toán đặt ra)
- **Phát hiện quá muộn**: Cố vấn học tập thường chỉ biết sinh viên gặp rủi ro học vụ (có nguy cơ rớt môn hoặc thôi học) khi học kỳ đã kết thúc và điểm thi cuối kỳ đã được công bố.
- **Can thiệp thiếu cá nhân hóa**: Giảng viên không có thời gian để phân tích nguyên nhân cụ thể của từng sinh viên (do hoàn cảnh gia đình, mất căn bản hay thiếu tính tự giác) để đưa ra kế hoạch hỗ trợ phù hợp.
- **Hành động thiếu kiểm soát**: Gửi các cảnh báo học vụ tự động từ hệ thống dễ gây áp lực tiêu cực lên sinh viên nếu không được cố vấn học tập kiểm duyệt nội dung trước khi gửi.

## 3. Targeted Solution (Giải pháp đề xuất)
Xây dựng một **Student Success Copilot** hỗ trợ cố vấn học tập:
1. **Dự đoán rủi ro (PyTorch Engine)**: Đánh giá xác suất rớt môn/thôi học (`risk_level`) và mức độ ưu tiên hỗ trợ (`priority_score`) dựa trên dữ liệu chuyên cần, điểm thi giữa kỳ và lịch sử nộp bài.
2. **Grounding học thuật (RAG)**: Tra cứu quy chế đào tạo, điều kiện nhận học bổng hoặc cảnh cáo học vụ để đưa ra phản hồi chuẩn xác cho sinh viên.
3. **Phê duyệt kế hoạch can thiệp (HITL)**: Kế hoạch can thiệp và cảnh cáo học vụ phải được CVHT phê duyệt trước khi gửi tin nhắn hỗ trợ đến sinh viên.
4. **Vận hành (Tool Call)**: Tự động ghi nhật ký can thiệp vào cơ sở dữ liệu học vụ sau khi được duyệt.
