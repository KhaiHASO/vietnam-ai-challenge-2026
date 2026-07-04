# Day-D Runbook: Hướng dẫn thực chiến 48 giờ

Tài liệu hướng dẫn từng bước dành cho cả đội khi Ban tổ chức công bố đề thi chính thức vào 11:00 AM ngày D-Day.

## Giờ 0 - 1: Phân tích Đề & Chốt Lĩnh vực (11:00 AM - 12:00 PM)
1. **Đọc kỹ đề bài**: Team Lead (Khải) tập hợp cả đội, đọc toàn bộ yêu cầu đầu ra, các điều khoản ràng buộc và dữ liệu được cung cấp.
2. **Chọn Domain thích hợp**:
   - Đối chiếu bài toán với 3 Domain Pack đã chuẩn bị sẵn (`sme`, `education`, `agriculture`).
   - Sử dụng bảng chấm điểm 10 tiêu chí trong [VAIC2026_Checklist_GiaiNhat_PyTorchAward.md](file:///C:/Users/Admin/Desktop/github/vietnam-ai-challenge-2026/VAIC2026_Checklist_GiaiNhat_PyTorchAward.md).
   - Chọn domain có số điểm cao nhất (tối thiểu 38/50 điểm). Không đổi đề sau khi đã chốt quá 6 tiếng.

## Giờ 1 - 3: Thiết lập Cấu hình & Dữ liệu (12:00 PM - 02:00 PM)
1. **Kích hoạt Domain**: Chạy lệnh switch domain để cập nhật cấu hình:
   ```bash
   python scripts/switch_domain.py <domain_name>
   ```
2. **Chuẩn bị Dữ liệu (Synthetic Data)**:
   - Sửa đổi cấu trúc file dữ liệu trong thư mục `domains/<domain_name>/data/` để khớp với schema dữ liệu mà đề bài yêu cầu.
   - Chạy script seed dữ liệu:
     ```bash
     python scripts/seed_domain.py --domain <domain_name> --train
     ```
     *(Lưu ý: Flag `--train` sẽ tự động kích hoạt huấn luyện baseline cho mô hình PyTorch Risk Engine để tránh lỗi import/loading).*

## Giờ 3 - 12: Tinh chỉnh AI Layer & Nghiệp vụ (02:00 PM - 11:00 PM)
1. **Nạp tri thức vào RAG**:
   - Biên soạn các quy chế chính thức từ đề thi vào tệp RAG trong `ai_layer/rag/knowledge_base.py` hoặc tệp json của domain.
   - Chạy lại lệnh seed để nạp lại vector database.
2. **Đăng ký Công cụ Nghiệp vụ (Tools)**:
   - Cập nhật các hàm API công cụ trong `ai_layer/tools/system_tools.py` để tương thích với cơ sở dữ liệu giả lập mới.
3. **Cập nhật Prompts**:
   - Hiệu chỉnh prompt của Agent Planner trong `ai_layer/agents/planner.py` để định hướng Agent suy nghĩ và đưa ra câu trả lời phù hợp với lĩnh vực mới.

## Giờ 12 - 24: Huấn luyện PyTorch Model & Tối ưu hóa (11:00 PM - 11:00 AM hôm sau)
1. **Huấn luyện mô hình**:
   - Chạy script train chính thức với số epoch lớn hơn để đạt độ chính xác cao:
     ```bash
     python -m ai_layer.pytorch_engine.train --domain <domain_name> --epochs 20 --batch_size 16
     ```
2. **Đánh giá & Benchmark**:
   - Chạy đánh giá để xuất tệp `metrics.json`:
     ```bash
     python -m ai_layer.pytorch_engine.evaluate --domain <domain_name>
     ```
   - Chạy đo latency để xuất `benchmark.json`:
     ```bash
     python -m ai_layer.pytorch_engine.benchmark --domain <domain_name>
     ```
3. **Xuất ONNX**:
   - Chạy xuất file ONNX phục vụ deploy/demo:
     ```bash
     python -m ai_layer.pytorch_engine.export_onnx --domain <domain_name>
     ```

## Giờ 24 - 36: Thiết kế UI & Demo Polish (11:00 AM - 11:00 PM)
1. **Cập nhật Giao diện Cockpit**:
   - Chỉnh sửa tiêu đề, logo và bảng thông tin metrics trên frontend để đồng bộ với domain mới.
   - Đảm bảo hiển thị trực quan điểm rủi ro của PyTorch, các căn cứ của RAG và nút bấm của hàng đợi phê duyệt (HITL Queue).
2. **Kiểm thử khép kín (End-to-End Test)**:
   - Chạy thử nghiệm 10 câu hỏi mẫu trong kịch bản demo để đảm bảo không bị lỗi API hay mất kết nối.

## Giờ 36 - 48: Tập luyện Thuyết trình & Đóng gói (11:00 PM - 11:00 AM ngày cuối)
1. **Quay video backup**: Thực hiện quay màn hình demo hoàn chỉnh dưới 5 phút làm phương án dự phòng nếu máy chiếu/hạ tầng mạng tại NIC gặp sự cố.
2. **Tập Pitching**: Presenter tập thuyết trình khớp với slide và demo thực tế trong 7 phút.
3. **Đóng gói mã nguồn**: Commit code lên GitHub public repository, chuẩn bị tài liệu kỹ thuật và nộp bài đúng cổng của Ban tổ chức trước 11:00 AM.
