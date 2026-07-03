# Risk and Mitigation Plan - CropCare AI Copilot

Các rủi ro vận hành, kỹ thuật nông nghiệp khi đưa AI vào canh tác thực địa và phương án giải quyết.

## 1. Rủi ro Chẩn đoán sai lầm (False Diagnosis)
- **Mô tả**: AI chẩn đoán sai loại bệnh (ví dụ: nhầm bệnh thiếu kẽm với nấm đạo ôn) dẫn đến việc khuyến nghị phun sai thuốc bảo vệ thực vật, gây ngộ độc cho cây.
- **Biện pháp khắc phục**:
  - Model PyTorch chỉ đưa ra cảnh báo "Nhóm triệu chứng nghi ngờ" kèm theo phần trăm tự tin (`confidence`).
  - Thiết lập cơ chế **Human-in-the-loop (HITL)**: Bất kỳ lệnh phun thuốc hóa học nào cũng yêu cầu kỹ sư nông nghiệp của HTX ký duyệt trực tiếp sau khi kiểm tra thực địa.

## 2. Rủi ro Lỗi Thiết bị Ngoại vi (IoT Hardware Failure)
- **Mô tả**: Cảm biến độ ẩm đất bị hỏng gửi dữ liệu sai lệch (ví dụ: cảm biến kẹt ở giá trị 100% ẩm dù đất khô cằn), khiến AI không tưới nước làm cây chết khô.
- **Biện pháp khắc phục**:
  - Tích hợp giải thuật kiểm tra chéo (Anomaly Detection) trên FastAPI backend. Nếu dữ liệu cảm biến không thay đổi liên tục trong 12 giờ, hệ thống sẽ tự động chuyển sang chế độ "sensor_degraded" và cảnh báo kỹ thuật.
  - Sử dụng chế độ tưới nước theo lịch trình cố định (Rule-based Fallback) khi cảm biến gặp sự cố.

## 3. Rủi ro Thiệt hại Môi trường (Environmental Impact)
- **Mô tả**: Tự động hóa quá mức dẫn đến việc xả nước hoặc phân bón quá lượng gây xói mòn và ô nhiễm nguồn nước ngầm xung quanh trang trại.
- **Biện pháp khắc phục**:
  - Giới hạn cứng lượng nước tưới tối đa và hàm lượng phân bón tối đa trong mã nguồn hệ thống (Hard Constraints).
  - RAG chỉ truy xuất các cẩm nang bón phân đạt chuẩn VietGAP/GlobalGAP để bảo đảm an toàn sinh học.
