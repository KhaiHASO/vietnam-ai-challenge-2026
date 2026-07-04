# Demo Script - Student Success Copilot (7 Minutes)

Kịch bản demo lĩnh vực Giáo dục.

## 0:00 - 0:45: Đặt vấn đề (Problem Statement)
* **Presenter**: "Chào Ban giám khảo, trong giáo dục, việc cố vấn học tập phát hiện sinh viên nợ môn quá muộn thường dẫn đến tỷ lệ thôi học tăng cao. CVHT bị quá tải và dữ liệu điểm số, chuyên cần của sinh viên lại nằm rải rác."

## 0:45 - 1:30: Giải pháp (Solution)
* **Presenter**: "Chúng em đề xuất **Student Success Copilot**. Hệ thống tự động phân tích dữ liệu học tập bằng PyTorch Risk Engine, truy xuất quy chế học vụ bằng RAG và đề xuất CVHT phê duyệt kế hoạch hỗ trợ sinh viên trước khi gửi đi."

## 1:30 - 3:30: Live Demo (Cảnh báo sinh viên vắng học)
* **Presenter**: "CVHT hỏi trợ lý ảo: *'Tuần này sinh viên STU-1002 Trần Thị B vắng mặt liên tiếp 3 buổi học phần Lập trình Python, hãy kiểm tra và đưa ra đề xuất.'*"
* **Thao tác**: Nhập câu hỏi vào chatbox.
* **Giải thích luồng Trace Flow**:
  1. **PII Scan**: Ẩn tên thật `Trần Thị B` và mã số sinh viên.
  2. **PyTorch Engine**: Đọc dữ liệu (GPA tích lũy: 2.1, Tỷ lệ chuyên cần: 65%, Bài nộp muộn: 5). Kết quả: `Risk Level: HIGH`, `Priority: 0.92`, `Needs Human Review: TRUE`.
  3. **RAG Grounding**: Truy xuất quy chế chuyên cần: *'Sinh viên vắng quá 20% tổng số giờ học phần sẽ bị đình chỉ thi...'*
  4. **HITL Trigger**: Hệ thống chặn hành động gửi cảnh báo chính thức vì rủi ro cao và đưa vào hàng đợi duyệt của CVHT.
  5. **AI Proposal**: AI đề xuất tin nhắn gửi cho sinh viên qua Zalo với giọng điệu động viên kèm đường link đăng ký lớp học phụ đạo bổ sung.

## 3:30 - 5:00: Phê duyệt của CVHT
* **Presenter**: "CVHT mở hàng đợi duyệt, xem lại các phân tích rủi ro của PyTorch, chỉnh sửa nhẹ tin nhắn và bấm **Approve**."
* **Thao tác**: Nhấn duyệt trên giao diện.
* **Kết quả**: Giao dịch chuyển sang `Approved`, hệ thống ghi nhận lịch sử can thiệp của sinh viên Trần Thị B vào cơ sở dữ liệu học tập.

## 5:00 - 6:00: Telemetry & Metrics
* **Presenter**: "Màn hình ghi nhận thời gian phản hồi của hệ thống chỉ mất **2.1 giây**. CVHT có thể dễ dàng quản lý 200 sinh viên cùng lúc mà không lo bỏ sót."

## 6:00 - 7:00: Chốt giá trị
* **Presenter**: "Hệ thống giúp CVHT chuyển từ chế độ đối phó thụ động sang chủ động can thiệp sớm, đồng hành cùng sự thành công của sinh viên. Em xin cảm ơn!"
