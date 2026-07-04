# Product Canvas - Student Success Copilot

## 1. User (Người dùng)
- **User trực tiếp**: Giảng viên, Cố vấn học tập (CVHT), Nhân viên phòng đào tạo.
- **Người ra quyết định**: Trưởng khoa, Ban giám hiệu nhà trường.
- **Người bị ảnh hưởng**: Sinh viên (đặc biệt là sinh viên có kết quả học tập kém).

## 2. Pain (Nỗi đau cốt lõi)
- CVHT bị quá tải, không thể theo dõi sát sao từng sinh viên.
- Dữ liệu chuyên cần và điểm số giữa kỳ nằm rời rạc trong file Excel của từng giảng viên.
- Cảnh báo học vụ gửi trễ khiến sinh viên không kịp cải thiện điểm số.
- Tin nhắn cảnh báo tự động quá khô khan, thiếu tính cá nhân hóa và động viên.

## 3. Current Workflow (Quy trình hiện tại)
1. Giảng viên chấm điểm giữa kỳ và điểm danh trên lớp.
2. Cuối kỳ, phòng đào tạo tổng hợp danh sách sinh viên có GPA < 2.0.
3. Phòng đào tạo gửi danh sách sinh viên bị cảnh cáo học vụ về cho CVHT.
4. CVHT liên lạc với từng sinh viên để tìm hiểu lý do (thường quá muộn để cứu vãn).

## 4. AI Role (Vai trò của AI)
- **Phân loại**: Chấm điểm rủi ro rớt môn (`high`, `medium`, `low`) bằng mô hình PyTorch Impact Triage dựa trên GPA học kỳ trước, tỷ lệ vắng và số bài tập nộp muộn.
- **Truy xuất**: RAG tìm quy chế đào tạo tương ứng (ví dụ: số buổi vắng tối đa được phép trước khi cấm thi).
- **Lập kế hoạch**: LLM Agent đề xuất kế hoạch can thiệp cá nhân hóa (như nhắc học nhóm, liên hệ giảng viên môn học).
- **Hành động**: Gọi công cụ ghi nhật ký can thiệp và chuẩn bị email hỗ trợ.

## 5. Data (Dữ liệu đầu vào)
- Dữ liệu điểm số, tỷ lệ chuyên cần, hoạt động LMS của lớp học.
- Ghi chú hoặc tin nhắn phản hồi của sinh viên (nếu có).

## 6. Output (Kết quả đầu ra)
- Đánh giá mức độ rủi ro rớt môn và độ ưu tiên từ PyTorch.
- Dự thảo email/tin nhắn nhắc nhở động viên sinh viên.
- Nhật ký can thiệp học vụ.

## 7. Human-in-the-loop (HITL)
- **Hành động cần duyệt**: Gửi thư cảnh báo học vụ chính thức hoặc các đề xuất đình chỉ học tập.
- **Người duyệt**: Cố vấn học tập/Trưởng khoa.
- **Cơ chế**: AI đề xuất email và kế hoạch học tập, CVHT chỉnh sửa nội dung và bấm nút phê duyệt để gửi đi.

## 8. Metrics (Chỉ số đo lường)
- Phát hiện sớm sinh viên có nguy cơ **trước kỳ thi cuối kỳ 4 tuần**.
- Tỷ lệ sinh viên cải thiện học lực sau can thiệp tăng trên **35%**.
- CVHT tiết kiệm **80%** thời gian soạn thảo tin nhắn hỗ trợ.

## 9. Risk (Rủi ro & Biện pháp)
- *Gây hoang mang*: AI chỉ đưa ra khuyến nghị hỗ trợ, CVHT đóng vai trò lọc câu chữ để tránh gây áp lực tâm lý cho sinh viên.
- *Lộ mã sinh viên/thông tin cá nhân*: Quét bảo mật PII để che giấu tên và MSSV trước khi gửi lên API LLM đám mây.
