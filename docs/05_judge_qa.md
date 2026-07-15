# Judge Q&A - Vietnam AI Innovation Challenge 2026

Tập hợp các câu hỏi khó từ Ban giám khảo và định hướng câu trả lời tối ưu để bảo vệ giải pháp.

## 1. Câu hỏi về AI-Native
### Q1: Giải pháp này khác gì một chatbot thông thường?
- **Trả lời**: "Chatbot thông thường chủ yếu trả lời văn bản tự do bằng LLM. Giải pháp của chúng em là một **AI-Native Agriculture Copilot & CropDoctor Platform**. Hệ thống nhận dữ liệu thật (ảnh chụp lá bệnh, triệu chứng, thời tiết), dùng mô hình PyTorch để phân loại và đánh giá mức độ nghiêm trọng của bệnh, dùng RAG để bám sát tài liệu hướng dẫn kỹ thuật nông nghiệp IPM, tự lập kế hoạch can thiệp thông qua 6 Agent tự trị, gọi các API để cập nhật nhật ký số và lên lịch theo dõi sau 48h, đồng thời đưa ra hàng đợi duyệt cho chuyên gia nếu cần sử dụng các biện pháp đặc biệt. Đây là một quy trình vận hành khép kín, an toàn và có kiểm soát."

### Q2: Tại sao không dùng Dashboard thông thường?
- **Trả lời**: "Dashboard thông thường chỉ mang tính mô tả tĩnh (mô tả những gì đã xảy ra). Hệ thống của chúng em là một Cockpit hành động chủ động: AI đọc dữ liệu thô, hiểu ngữ cảnh thời gian thực, dự đoán rủi ro, khuyến nghị hành động tiếp theo và tạo sẵn nhật ký/nội dung phản hồi. Nó trực tiếp hỗ trợ người vận hành ra quyết định nhanh hơn thay vì chỉ hiển thị số liệu."

---

## 2. Câu hỏi về Kỹ thuật PyTorch
### Q3: Tại sao lại dùng PyTorch để tính điểm rủi ro, dùng LLM phân loại luôn có được không?
- **Trả lời**: "Dùng LLM để phân loại rủi ro gặp ba vấn đề lớn: (1) Độ trễ (latency) cao (thường từ 2-4 giây) so với chỉ **1.2 miligiây** của PyTorch; (2) Chi phí gọi API LLM lớn khi quét hàng loạt ảnh bệnh/vết bệnh; (3) LLM không ổn định (nhiễu kết quả đầu ra). PyTorch Multi-task Engine của chúng em giải quyết cả ba vấn đề: chạy cực nhanh trên CPU cục bộ, chi phí bằng 0, đầu ra ổn định và có thể kiểm chứng toán học bằng F1-score."

### Q4: Mô hình PyTorch này được huấn luyện bằng dữ liệu gì? Có đáng tin cậy không?
- **Trả lời**: "Trong thời gian 48h của Hackathon, chúng em sử dụng dữ liệu mô phỏng được tạo sinh (synthetic data) dựa trên các tham số nghiệp vụ thực tế và có bổ sung nhiễu để chứng minh tính khả thi của quy trình. Lộ trình của chúng em có giai đoạn **Shadow Mode (chế độ chạy bóng tối)** trong tuần đầu tiên khi pilot. Chúng em sẽ chạy song song mô hình để thu thập dữ liệu thật và tinh chỉnh trọng số (fine-tune) trước khi kích hoạt hoàn toàn trong vận hành."

---

## 3. Câu hỏi về Khả năng Triển khai (Pilot & Scale)
### Q5: Làm sao tích hợp được hệ thống này vào các doanh nghiệp nhỏ khi họ không có hạ tầng IT mạnh?
- **Trả lời**: "Chúng em thiết kế hệ thống tách biệt hoàn toàn giữa lõi AI điều phối, bối cảnh vùng trồng và cơ sở dữ liệu. Nông dân và hợp tác xã chỉ cần tải ảnh lá cây hoặc kết nối qua kênh Zalo/Telegram nông nghiệp cơ bản. Giai đoạn đầu, pilot sẽ hoạt động độc lập (stand-alone) qua giao diện Cockpit của chúng em, sau đó mới tích hợp sâu vào hệ thống quản lý sản xuất của hợp tác xã."

### Q6: Nếu AI dự đoán sai dẫn đến hành động sai thì sao?
- **Trả lời**: "Hệ thống thiết lập chốt bảo vệ an toàn **Human-in-the-loop (HITL)**. Các hành động rủi ro như đề xuất phun hóa chất liều cao hoặc cập nhật nhật ký bệnh án diện rộng bắt buộc phải nằm ở trạng thái chờ duyệt (Pending). AI chỉ chuẩn bị thông tin và khuyến nghị kỹ thuật, quyền nhấn nút thực thi/duyệt cuối cùng luôn thuộc về chuyên gia nông nghiệp hoặc chủ vườn."
