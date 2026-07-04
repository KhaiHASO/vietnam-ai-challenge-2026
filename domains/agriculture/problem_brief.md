# Problem Brief: CropCare AI Copilot (Agriculture Domain)

## 1. Context (Bối cảnh)
Trong nông nghiệp công nghệ cao và canh tác chính xác, nông dân và chủ trang trại phải quản lý hàng ngàn cây trồng trên diện tích lớn. Việc phát hiện sâu bệnh gây hại, thiếu nước, hay lạm dụng phân bón hóa học thường phụ thuộc hoàn toàn vào kinh nghiệm thủ công.

## 2. Problem Statement (Bài toán đặt ra)
- **Thiệt hại lan rộng**: Phát hiện bệnh hại trễ khiến dịch bệnh lây lan toàn vườn, gây thiệt hại nghiêm trọng đến sản lượng và doanh thu mùa vụ.
- **Tri thức phân tán**: Thông tin kỹ thuật nông nghiệp thường nằm ở các tài liệu nghiên cứu dày cộp, cẩm nang khuyến nông hoặc kinh nghiệm của đại lý bán thuốc bảo vệ thực vật, khó tiếp cận nhanh.
- **Rủi ro môi trường**: Sử dụng hóa chất diệt nấm/sâu hại tự động, quá liều hoặc sai thời điểm ảnh hưởng đến an toàn thực phẩm, sức khỏe đất và chi phí vận hành.

## 3. Targeted Solution (Giải pháp đề xuất)
Xây dựng một **CropCare AI Copilot** hỗ trợ chủ vườn:
1. **Đánh giá sức khỏe (PyTorch Engine)**: Sử dụng mô hình PyTorch (tích hợp xử lý ảnh lá cây hoặc chỉ số cảm biến đất) để phân loại mức độ nghiêm trọng (`severity_level`) và rủi ro sâu bệnh (`risk_level`).
2. **Tri thức nông nghiệp (RAG)**: Truy xuất nhanh cẩm nang phòng trừ dịch hại VietGAP để đưa ra khuyến nghị xử lý an toàn sinh học.
3. **Phê duyệt đơn thuốc (HITL)**: Các hành động đề xuất phun thuốc hóa học độc hại phải được chuyên gia nông nghiệp hoặc chủ vườn phê duyệt trước khi ghi vào nhật ký vận hành.
4. **Vận hành (Tool Call)**: Ghi lại lịch sử điều trị vườn trồng và kích hoạt hệ thống tưới tự động (nếu có).
