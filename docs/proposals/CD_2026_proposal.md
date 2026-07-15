# Proposal: Nâng Cấp Luồng Chẩn Đoán Thực Tế Lầm Sàng Cho CropDoctor AI

## 1. Mục tiêu
Thiết lập quy trình lâm sàng thực tế khép kín cho CropDoctor AI, đưa sản phẩm từ mức độ "nhận diện ảnh" (Google Lens) lên mức độ "trợ lý điều tra và điều hành sức khỏe cây trồng".

## 2. Phạm vi nâng cấp (6 Tính năng cốt lõi)
1.  **Chẩn đoán chủ động đa bằng chứng**: Hệ thống đưa ra 2-3 giả thuyết hàng đầu và tự sinh câu hỏi phân biệt dựa trên thời tiết, mùa vụ, lịch sử chăm sóc.
2.  **AI biết từ chối**: Phân tích độ tương phản/độ sáng bằng PIL & Numpy, từ chối ảnh kém chất lượng và hướng dẫn chụp lại hoặc chuyển chuyên gia.
3.  **Giải thích bằng chứng**: Hiển thị bằng chứng ủng hộ bệnh ưu tiên và bằng chứng chống lại các khả năng khác.
4.  **Kế hoạch IPM an toàn**: Phân tầng 3 lớp: Canh tác vật lý ngay lập tức, theo dõi, và can thiệp hóa chất (cần phê duyệt).
5.  **Vòng lặp theo dõi 48h**: Lên lịch chụp ảnh đối chiếu trước-sau để đánh giá sự thuyên giảm của vết bệnh.
6.  **Cảnh báo ổ dịch**: Tự động tổng hợp các ca bệnh giống nhau xuất hiện gần nhau để cảnh báo dịch cấp hợp tác xã.

## 3. Rủi ro & Giải pháp dự phòng
- *Rủi ro*: Không có API Key DeepSeek hoặc mất mạng trong buổi demo.
- *Giải pháp*: Tích hợp cơ chế local rules fallback thông minh trong python backend trả về kết quả lập luận nông nghiệp và IPM đầy đủ.
