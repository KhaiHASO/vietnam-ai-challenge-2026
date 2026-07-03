# Product Canvas - CropCare AI Copilot

## 1. User (Người dùng)
- **User trực tiếp**: Nông dân, Kỹ thuật viên nông nghiệp tại trang trại.
- **Người ra quyết định**: Chủ vườn, Hợp tác xã nông nghiệp.
- **Người bị ảnh hưởng**: Người tiêu dùng nông sản, Môi trường đất/nước xung quanh trang trại.

## 2. Pain (Nỗi đau cốt lõi)
- Nông dân khó nhận biết chính xác triệu chứng bệnh trên lá cây lúc mới chớm.
- Lạm dụng thuốc bảo vệ thực vật gây tốn chi phí và ảnh hưởng chất lượng xuất khẩu.
- Thiếu cẩm nang xử lý dịch bệnh VietGAP trực quan tại chỗ.
- Hệ thống tưới tiêu hoạt động thiếu chính xác theo thời tiết và độ ẩm đất.

## 3. Current Workflow (Quy trình hiện tại)
1. Nông dân đi tuần tra vườn, phát hiện lá vàng úa hoặc sâu hại bằng mắt thường.
2. Nông dân tự chẩn đoán dựa trên kinh nghiệm cá nhân hoặc chụp ảnh hỏi đại lý thuốc bảo vệ thực vật gần nhà.
3. Nông dân mua và phun thuốc theo chỉ dẫn của đại lý (dễ bị mua quá liều lượng cần thiết).
4. Khó ghi nhận nhật ký bón phân/phun thuốc đồng bộ phục vụ truy xuất nguồn gốc.

## 4. AI Role (Vai trò của AI)
- **Phân loại**: Đánh giá mức độ tổn hại của cây (`leaf_damage_percent`) và rủi ro lây lan dịch bệnh bằng mô hình PyTorch Multi-Task.
- **Truy xuất**: RAG tìm kiếm chính sách điều trị an toàn sinh học từ cẩm nang khuyến nông.
- **Lập kế hoạch**: LLM Agent soạn lịch trình chăm sóc, phục hồi cây trồng trong 7 ngày tới.
- **Hành động**: Gọi công cụ tự động lưu nhật ký điều trị và kích hoạt rơ-le tưới nước tự động.

## 5. Data (Dữ liệu đầu vào)
- Ảnh chụp triệu chứng bệnh trên cây hoặc mô tả văn bản.
- Metadata cảm biến IoT: Nhiệt độ không khí, độ ẩm đất, lượng mưa dự kiến, số ngày kể từ lần phun thuốc gần nhất.

## 6. Output (Kết quả đầu ra)
- Điểm đánh giá rủi ro cây trồng và độ ưu tiên từ PyTorch.
- Kế hoạch bón phân/tưới nước 7 ngày tối ưu.
- Lệnh kích hoạt thiết bị IoT chờ duyệt trên HITL Queue.

## 7. Human-in-the-loop (HITL)
- **Hành động cần duyệt**: Khuyến nghị sử dụng các hóa chất diệt nấm cực mạnh hoặc kích hoạt hệ thống phun thuốc đại trà.
- **Người duyệt**: Chuyên gia bảo vệ thực vật hoặc Chủ vườn.
- **Cơ chế**: AI đề xuất danh mục thuốc và nồng độ pha chế, chuyên gia kiểm duyệt và bấm **Approve** để phê duyệt đưa vào áp dụng.

## 8. Metrics (Chỉ số đo lường)
- Giảm chi phí sử dụng thuốc bảo vệ thực vật từ **20-30%**.
- Tăng tỷ lệ phát hiện bệnh hại sớm lên **95%** nhờ hỗ trợ của AI.
- 100% nhật ký bón phân/phun thuốc được lưu trữ chuẩn hóa VietGAP để phục vụ truy xuất nguồn gốc nông sản.

## 9. Risk (Rủi ro & Biện pháp)
- *Chẩn đoán sai bệnh*: AI không tự ý đưa ra kết luận khẳng định; RAG luôn kèm theo khuyến nghị "chờ chuyên gia đối chứng trực tiếp".
- *Mất kết nối Internet*: Hệ thống hỗ trợ chế độ offline chạy mô hình PyTorch cục bộ trên thiết bị di động (Edge AI) thông qua ONNX runtime.
