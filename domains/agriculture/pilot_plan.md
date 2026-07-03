# Pilot Pathway: CropCare AI Copilot

Lộ trình thử nghiệm thực tế giải pháp **CropCare AI Copilot** tại 1 Hợp tác xã trồng trọt trong thời gian 2 tuần.

## 1. Phase 1: Setup & Baseline Eval (Ngày 1 - 3)
- **Mục tiêu**: Lắp đặt cảm biến độ ẩm đất và thu thập 150 hình ảnh mẫu bệnh hại cây trồng của HTX.
- **Hành động**:
  - Nhập cẩm nang chăm sóc và phòng trừ sâu bệnh của cây durian/rice vào Vector DB.
  - Huấn luyện mô hình PyTorch Risk Engine dựa trên dữ liệu ảnh và cảm biến.
- **Tiêu chí đạt**: Mô hình đạt F1-score > 0.85 trong việc phân loại các mức độ nghiêm trọng của bệnh hại.

## 2. Phase 2: Shadow Mode (Ngày 4 - 7)
- **Mục tiêu**: AI chạy thử nghiệm ghi nhận thông tin vườn mà không can thiệp trực tiếp vào lịch chăm sóc của nông dân.
- **Hành động**:
  - Nông dân chụp ảnh cây bệnh hàng ngày gửi qua app. AI đề xuất phác đồ điều trị và lưu nháp lịch trình tưới nước.
  - Kỹ thuật viên đối chiếu đề xuất của AI với thực tế.
- **Tiêu chí đạt**: AI phát hiện đúng 100% các trường hợp cây bị khô hạn nặng hoặc nhiễm bệnh nghiêm trọng (Zero False Negatives cho rủi ro High).

## 3. Phase 3: Limited Pilot (Ngày 8 - 14)
- **Mục tiêu**: Kích hoạt hành động có kiểm soát bởi AI trên một khu vực thử nghiệm 0.5ha.
- **Hành động**:
  - Tích hợp rơ-le thông minh vào van tưới nước. AI tính toán lịch tưới tối ưu và gửi yêu cầu phê duyệt tưới lên điện thoại chủ vườn.
  - Nông dân duyệt lệnh tưới và duyệt danh mục thuốc trừ sâu sinh học do AI khuyến nghị thông qua HITL Queue.
- **Tiêu chí đạt**:
  - Tiết kiệm **25%** lượng nước tưới so với phương pháp thủ công.
  - 100% lịch sử xử lý dịch bệnh được ghi nhận tự động vào nhật ký canh tác điện tử của HTX.

## 4. Phase 4: Production (Sau tuần 2)
- Mở rộng lắp đặt cho toàn bộ các lô đất canh tác trong Hợp tác xã.
- Tích hợp thêm module dự báo thời tiết của khí tượng thủy văn để tự động điều chỉnh lượng nước tưới đón đầu lượng mưa.
