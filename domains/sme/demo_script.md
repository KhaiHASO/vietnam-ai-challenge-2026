# Demo Script - SME Operations Copilot (7 Minutes)

Kịch bản demo luồng xử lý chính trong 7 phút phục vụ Ban giám khảo.

## 0:00 - 0:45: Đặt vấn đề (Problem Statement)
* **Presenter**: "Kính thưa Ban giám khảo, vấn đề của các doanh nghiệp nhỏ cung cấp dịch vụ không phải là thiếu chatbot. Nỗi đau thực sự của họ là dữ liệu vận hành bị cô lập, nhân viên trực quầy quá tải khi xử lý sự cố thanh toán và nguy cơ thất thoát tài chính khi cho phép nhân viên tự hoàn tiền."

## 0:45 - 1:30: Giải pháp & Kiến trúc (Architecture)
* **Presenter**: "Chúng em xin giới thiệu **SME Operations Copilot** – Trợ lý vận hành AI-native. Hệ thống kết hợp mô hình PyTorch Risk Engine để phân loại rủi ro, RAG để bám sát chính sách và chốt bảo vệ Human-in-the-loop để kiểm soát giao dịch tài chính."

## 1:30 - 3:30: Live Demo Main Flow (Hủy sân & Hoàn tiền MoMo)
* **Presenter**: "Bây giờ em sẽ gửi một yêu cầu của khách hàng: *'Tôi muốn hủy lịch đặt sân Pickleball mã BKG-88321A tối nay lúc 18h và hoàn tiền ví Momo cho tôi, số điện thoại của tôi là 0912345678'*"
* **Thao tác**: Nhập câu truy vấn vào chatbox.
* **Giải thích các bước hiển thị trên Cockpit Trace Flow**:
  1. **Bước 1**: Số điện thoại `0912345678` lập tức được quét và chuyển thành `[REDACTED]` để bảo mật PII.
  2. **Bước 2**: PyTorch Engine chạy ngầm và đánh giá: `Risk Level: HIGH`, `Priority: 0.88`, `Needs Human Review: TRUE`.
  3. **Bước 3**: RAG truy xuất chính sách: *'Đối với các thanh toán qua Ví điện tử Momo từ 500,000 VND trở lên yêu cầu người quản trị (Admin) phê duyệt thủ công...'*
  4. **Bước 4**: Do PyTorch đánh giá rủi ro cao và cần phê duyệt, hệ thống kích hoạt **Human-in-the-loop** và đóng băng lệnh hoàn tiền dưới trạng thái `Pending Approval`.
  5. **Bước 5**: AI soạn thảo sẵn câu trả lời đã khôi phục số điện thoại để gửi cho khách hàng, thông báo giao dịch đang chờ quản trị viên phê duyệt.

## 3:30 - 5:00: Phê duyệt của Admin (HITL Cockpit)
* **Presenter**: "Chuyển sang màn hình của Admin. Chúng ta thấy yêu cầu hoàn tiền cho mã BKG-88321A đang nằm trong hàng đợi duyệt. Admin kiểm tra các yếu tố rủi ro do PyTorch phân tích và nhấn **Approve**."
* **Thao tác**: Nhấn **Approve** trên giao diện duyệt.
* **Kết quả**: Giao dịch chuyển sang `Approved`, số dư ví của khách hàng giả định được hoàn trả tự động và ghi nhật ký kiểm toán (audit log).

## 5:00 - 6:00: Các chỉ số vận hành (Telemetry & Metrics)
* **Presenter**: "Tại góc phải màn hình, dashboard ghi nhận thời gian xử lý được rút ngắn xuống chỉ còn **18 giây** thay vì 15 phút như trước đây. Telemetry log hiển thị chi tiết độ trễ của từng bước (PII: 2ms, PyTorch: 1.2ms, RAG: 15ms)."

## 6:00 - 7:00: Chốt giá trị (Value Proposition)
* **Presenter**: "Hệ thống của chúng em chứng minh rằng: AI không thay thế con người đưa ra quyết định rủi ro, mà AI đóng vai trò chuẩn bị thông tin, định tuyến thông minh và tự động hóa các tác vụ lặp lại để doanh nghiệp vận hành an toàn và tối ưu nhất. Em xin cảm ơn!"
