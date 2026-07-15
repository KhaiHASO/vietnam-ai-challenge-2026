# ADR 001: Triển Khai 6 Tính Năng Sát Thủ Cho CropDoctor AI

*   **Status**: Proposed
*   **Deciders**: Đội ngũ phát triển CropDoctor AI
*   **Date**: 2026-07-10

## Context (Bối cảnh)
Sản phẩm CropDoctor AI tham dự cuộc thi VAIC 2026 hiện tại đã đầy đủ các trang và giao diện công nghệ cơ bản (Vision Agent, Symptom Agent, Reasoning Agent...). Tuy nhiên, sản phẩm đang thiếu một **"tính năng sát thủ"** kết nối chặt chẽ các thành phần để giải quyết trọn vẹn quy trình chẩn đoán lâm sàng thực tế: từ chẩn đoán sơ bộ, hỏi triệu chứng phân biệt, từ chối ảnh kém chất lượng, IPM 3 tầng an toàn, theo dõi 48 giờ đến cảnh báo dịch cấp hợp tác xã.

## Options Considered (Các phương án xem xét)
1.  **Phương án A**: Tiếp tục thêm nhiều màn hình dashboard phụ và tăng số lượng Agent độc lập (gây loãng sản phẩm, biến thành bộ demo công nghệ thiếu tính ứng dụng).
2.  **Phương án B (Lựa chọn)**: Tập trung hoàn thiện quy trình thực tế qua 6 tính năng cốt lõi:
    - *Chẩn đoán chủ động đa bằng chứng*: Tự động đề xuất câu hỏi phân biệt dựa trên 2-3 giả thuyết.
    - *AI biết từ chối*: Sử dụng PIL & Numpy phân tích pixel ảnh để từ chối ảnh mờ/tối thực tế.
    - *Chẩn đoán phân biệt*: Hiển thị rõ bằng chứng ủng hộ/chống lại từng giả thuyết.
    - *Kế hoạch IPM an toàn*: Phân tầng 3 lớp xử lý, chuyển các đề xuất hóa chất rủi ro vào hàng chờ duyệt.
    - *Vòng lặp theo dõi 48 giờ*: Cho phép nông dân cập nhật ảnh sau 48h để so sánh tiến triển vết bệnh.
    - *Cảnh báo ổ dịch*: Tự động phát hiện các ca bệnh tương tự xuất hiện gần nhau kết hợp điều kiện thời tiết độ ẩm cao để cảnh báo ổ dịch cấp hợp tác xã.

## Decision (Quyết định)
Lựa chọn **Phương án B** để nâng tầm sản phẩm từ ứng dụng nhận diện ảnh đơn thuần thành một **hệ thống điều hành sức khỏe cây trồng**.

## Consequences (Hệ quả)
- Đảm bảo tính ứng dụng cao, đáp ứng các tiêu chí chấm điểm của VAIC 2026.
- Đòi hỏi cập nhật lại logic xử lý của `VisionService`, `ReasoningAgent`, và hệ thống database/API.
- Đảm bảo demo live mượt mà kể cả khi ngoại tuyến hoặc không có API Key nhờ cơ chế Fallback thông minh.
