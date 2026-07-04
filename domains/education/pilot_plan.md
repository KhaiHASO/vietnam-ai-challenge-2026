# Pilot Pathway: Student Success Copilot

Lộ trình thử nghiệm thực tế giải pháp **Student Success Copilot** tại 1 Khoa đào tạo trong thời gian 2 tuần.

## 1. Phase 1: Preparation & Evaluation (Ngày 1 - 3)
- **Mục tiêu**: Thu thập dữ liệu học tập lịch sử của 300 sinh viên khóa trước để đánh giá mô hình.
- **Hành động**:
  - Tải quy chế học vụ và cẩm nang sinh viên vào Vector DB.
  - Huấn luyện mô hình PyTorch Risk Engine để nhận dạng các yếu tố kết hợp dẫn đến rớt môn (ví dụ: vắng > 2 buổi và điểm quiz < 5).
- **Tiêu chí đạt**: Mô hình PyTorch đạt F1-score > 0.88 trong việc phân loại sinh viên có nguy cơ cao.

## 2. Phase 2: Shadow Mode (Ngày 4 - 7)
- **Mục tiêu**: CVHT chạy thử nghiệm hệ thống song song với công việc thực tế để kiểm chứng độ chính xác.
- **Hành động**:
  - Mỗi tuần, hệ thống tự động quét dữ liệu LMS và chuyên cần của 2 lớp học mẫu để xuất báo cáo rủi ro.
  - CVHT so sánh danh sách dự báo của AI với cảm nhận thực tế của mình để hiệu chỉnh trọng số mô hình.
- **Tiêu chí đạt**: Tỷ lệ trùng khớp giữa dự báo của AI và đánh giá của CVHT đạt trên **85%**.

## 3. Phase 3: Limited Pilot (Ngày 8 - 14)
- **Mục tiêu**: Thực hiện can thiệp học vụ thực tế trên nhóm sinh viên được xác định rủi ro.
- **Hành động**:
  - AI phát hiện sinh viên vắng học hoặc điểm thấp, soạn sẵn kế hoạch cải thiện điểm số và tin nhắn nhắc nhở.
  - CVHT duyệt và gửi tin nhắn qua Zalo/Email cho sinh viên.
  - Tổ chức các buổi phụ đạo ngắn dựa trên gợi ý tài liệu học tập của RAG.
- **Tiêu chí đạt**:
  - 100% sinh viên có nguy cơ cao nhận được hỗ trợ kịp thời trước kỳ thi cuối kỳ.
  - Tỷ lệ sinh viên phản hồi tích cực và tham gia phụ đạo đạt trên **70%**.

## 4. Phase 4: Full Scaling (Sau tuần 2)
- Triển khai áp dụng cho toàn bộ các khoa đào tạo trong trường.
- Tích hợp cổng thông tin tự động liên hệ phụ huynh đối với các trường hợp đặc biệt nghiêm trọng (sau khi có sự đồng ý của CVHT).
