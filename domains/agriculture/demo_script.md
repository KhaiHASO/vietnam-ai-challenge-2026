# Demo Script - CropCare AI Copilot (7 Minutes)

Kịch bản demo lĩnh vực Nông nghiệp.

## 0:00 - 0:45: Đặt vấn đề (Problem Statement)
* **Presenter**: "Kính thưa Ban giám khảo, trong nông nghiệp chính xác, việc phát hiện dịch bệnh hại cây trễ chỉ vài ngày có thể làm mất trắng sản lượng cả một vườn sầu riêng. Nông dân thiếu cẩm nang chẩn đoán chính xác tại chỗ và thường lạm dụng hóa chất độc hại gây ảnh hưởng môi trường."

## 0:45 - 1:30: Giải pháp (Solution)
* **Presenter**: "Chúng em xin giới thiệu **CropCare AI Copilot** – Trợ lý giám sát nông nghiệp thông minh. Giải pháp dùng PyTorch để đánh giá tổn thương của lá cây và dữ liệu cảm biến, dùng RAG để tra cứu phác đồ điều trị VietGAP và quản lý hành động phun thuốc thông qua Human-in-the-loop."

## 1:30 - 3:30: Live Demo (Phát hiện bệnh hại durian)
* **Presenter**: "Nông dân gửi thông báo khẩn: *'Vườn sầu riêng của tôi ở Lô A mã FRM-502 phát hiện vệt đốm nâu hình quả trám lan rộng trên lá lúa nghi ngờ bị đạo ôn nặng, cần phun thuốc điều trị gấp.'*"
* **Thao tác**: Nhập câu truy vấn vào chatbox.
* **Giải thích luồng Trace Flow**:
  1. **PII Scan**: Lọc bỏ các thông tin tọa độ chi tiết hoặc thông tin sở hữu cá nhân.
  2. **PyTorch Engine**: Nhập dữ liệu (Tổn thương lá: 45%, Nhiệt độ: 33.5C, Độ ẩm đất: 32%, Số ngày chưa tưới: 18). Kết quả: `Risk Level: HIGH`, `Priority: 0.96`, `Needs Human Review: TRUE`.
  3. **RAG Grounding**: Truy xuất hướng dẫn dịch hại: *'Bệnh nấm đạo ôn phát triển mạnh trong ẩm độ cao... nếu tổn thương lá >10% phun thuốc Tricyclazole... việc dùng hóa chất này cần chuyên gia xác nhận...'*
  4. **HITL Trigger**: Hệ thống nhận dạng đây là tác vụ phun hóa chất độc hại có mức độ rủi ro rất cao nên đã tự động đưa khuyến nghị vào hàng đợi duyệt `Pending Approval`.
  5. **AI Proposal**: AI đề xuất câu trả lời chuẩn bị sẵn phác đồ điều trị sinh học thay thế tạm thời và hướng dẫn nông dân chờ chuyên gia nông nghiệp đến xác duyệt.

## 3:30 - 5:00: Phê duyệt của Chuyên gia
* **Presenter**: "Kỹ sư nông nghiệp của HTX mở ứng dụng Cockpit, kiểm tra ảnh chụp và thông số rủi ro do PyTorch tính toán, nhấn **Approve** cho phép sử dụng liều lượng thuốc Tricyclazole tối thiểu."
* **Thao tác**: Nhấn duyệt.
* **Kết quả**: Giao dịch chuyển sang `Approved`, lưu nhật ký kiểm tra truy xuất nguồn gốc.

## 5:00 - 6:00: Telemetry & IoT Metrics
* **Presenter**: "Hệ thống ghi nhận thời gian phản hồi cực nhanh chỉ **1.8 giây**. Báo cáo lượng hóa chất sử dụng trong HTX giảm rõ rệt giúp tiết kiệm **25%** chi phí bảo vệ thực vật."

## 6:00 - 7:00: Chốt giá trị
* **Presenter**: "CropCare AI Copilot mang đến mô hình canh tác bền vững: AI hỗ trợ chẩn đoán, con người kiểm soát hóa chất độc hại, hướng tới nông nghiệp xanh chất lượng cao. Em xin cảm ơn!"
