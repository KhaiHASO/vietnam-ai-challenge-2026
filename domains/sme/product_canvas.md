# Product Canvas - SME Operations Copilot

## 1. User (Người dùng)
- **User trực tiếp**: Nhân viên trực quầy chăm sóc khách hàng, nhân viên vận hành sân bãi.
- **Người ra quyết định**: Chủ doanh nghiệp nhỏ (SME Owner), Quản lý cơ sở.
- **Người bị ảnh hưởng**: Khách hàng thuê sân/dịch vụ.

## 2. Pain (Nỗi đau cốt lõi)
- Dữ liệu nằm rời rạc ở nhiều ứng dụng (Zalo, Excel, Ví điện tử).
- Nhân viên mất trung bình 10-15 phút để tra chính sách và phản hồi một sự cố thanh toán.
- Bỏ sót khiếu nại của khách hàng quan trọng.
- Thao tác hoàn tiền rủi ro bị lạm dụng nếu không được kiểm soát.

## 3. Current Workflow (Quy trình hiện tại)
1. Khách hàng nhắn tin báo lỗi trừ tiền MoMo trên fanpage/Zalo.
2. Nhân viên đọc tin nhắn, chụp màn hình gửi nhóm quản lý duyệt.
3. Nhân viên đối chiếu thủ công trong Excel hoặc admin portal ví điện tử.
4. Nhân viên phản hồi khách hàng và cập nhật thủ công vào file Excel.

## 4. AI Role (Vai trò của AI)
- **Phân loại**: Chấm điểm mức độ rủi ro (Risk) và độ ưu tiên (Priority) dựa trên thông tin khiếu nại bằng mô hình PyTorch Multi-Task.
- **Truy xuất**: RAG tìm chính sách hoàn tiền tương ứng dựa trên thời gian hủy và kênh thanh toán.
- **Lập kế hoạch**: LLM Agent ReAct nhận diện hành động cần làm (tạo ticket hỗ trợ hoặc gửi duyệt hoàn tiền).
- **Hành động**: Gọi công cụ nghiệp vụ cập nhật cơ sở dữ liệu.

## 5. Data (Dữ liệu đầu vào)
- Tin nhắn khiếu nại/yêu cầu của khách hàng (Unstructured text).
- Metadata giao dịch: Mã booking, số tiền, hạng thành viên, số lượng ticket lỗi đang chờ.

## 6. Output (Kết quả đầu ra)
- Điểm đánh giá rủi ro nghiệp vụ (`low`, `medium`, `high`) từ PyTorch.
- Dự thảo tin nhắn phản hồi đã grounding theo chính sách.
- Ticket hỗ trợ tự động được tạo.
- Giao dịch chờ duyệt trên Admin HITL Queue.

## 7. Human-in-the-loop (HITL)
- **Hành động cần duyệt**: Hủy đặt chỗ cận giờ, hoàn tiền ví điện tử (các giao dịch tài chính).
- **Người duyệt**: Quản trị viên/Chủ doanh nghiệp.
- **Cơ chế chặn**: AI đề xuất và chuẩn bị sẵn payload hành động, trạng thái đặt là `pending_approval` cho đến khi admin nhấn nút `Approve`.

## 8. Metrics (Chỉ số đo lường)
- Giảm thời gian xử lý khiếu nại trung bình từ **15 phút xuống dưới 2 phút** (Cải thiện >85%).
- Tỷ lệ bỏ sót khiếu nại tài chính giảm về **0%**.
- Tỷ lệ duyệt thành công đề xuất của AI từ admin đạt trên **90%**.

## 9. Risk (Rủi ro & Biện pháp)
- *Ảo tưởng của LLM*: Dùng Output Guardrail kiểm tra điểm Hallucination so với chính sách gốc trước khi hiển thị.
- *Lộ dữ liệu cá nhân*: Quét và che giấu (redact) thông tin PII trước khi gửi lên LLM đám mây.
