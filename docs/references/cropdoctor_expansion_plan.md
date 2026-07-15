# 🩺 CropDoctor AI & Copilot: Tài Liệu Tính Năng Hiện Có & Lộ Trình Nâng Cấp Hệ Thống

Tài liệu này đóng vai trò là Cẩm nang Kỹ thuật (Technical Reference) và Lộ trình Nâng cấp (Feature Roadmap) chính thức của dự án tham gia cuộc thi **Vietnam AI Innovation Challenge (VAIC) 2026**.

---

## 🧱 PHẦN 1: TỔNG QUAN HỆ THỐNG & CÁC TÍNH NĂNG HIỆN CÓ

Hệ thống được thiết kế theo mô hình **AI-Native Software**, kết hợp giữa phân loại rủi ro nghiệp vụ bằng PyTorch và chẩn đoán dịch bệnh lâm sàng đa tác nhân (Multi-Agent).

### 🤖 1. Luồng 6 AI Agent Tự Trị (CropDoctor Clinical Pipeline)
Khi nông dân gửi ảnh chụp lá/quả bệnh lên hệ thống, luồng chẩn đoán sẽ kích hoạt 6 AI Agent chạy nối tiếp nhau để thu thập và hợp nhất tri thức:

1.  **Vision Consensus Agent (Thị giác máy tính):**
    *   *Nhiệm vụ:* Sử dụng mô hình thị giác phân tích cấu trúc hình ảnh lá/quả bệnh.
    *   *Tham số đầu ra:*
        *   `lesion_count`: Số lượng vết bệnh phát hiện (ví dụ: `14` vết).
        *   `leaf_area_affected`: Tỷ lệ phần trăm diện tích bề mặt lá bị hư hại (ví dụ: `18%`).
        *   `image_quality`: Trắc lượng chất lượng ảnh chụp (ví dụ: `0.91`).
2.  **Symptom Agent (Thu thập triệu chứng lâm sàng):**
    *   *Nhiệm vụ:* Bóc tách các triệu chứng bổ sung do nông dân nhập dưới dạng ngôn ngữ tự nhiên.
    *   *Tham số đầu ra:*
        *   `rain_after`: Có mưa kéo dài sau khi xuất hiện bệnh không (`true/false`).
        *   `fruit_spots`: Vết bệnh đã lan sang quả chưa (`true/false`).
        *   `spread_speed`: Tốc độ lây lan trong vườn (`slow/medium/fast`).
3.  **Context Agent (Tra cứu bối cảnh khí tượng):**
    *   *Nhiệm vụ:* Kết nối dữ liệu bối cảnh thời tiết của vùng canh tác (Trảng Bom, Long Thành, Đồng Nai).
    *   *Tham số đầu ra:*
        *   `humidity`: Độ ẩm không khí đo được (ví dụ: `89%`).
        *   `rainfall`: Lượng mưa tích lũy (ví dụ: `42mm`).
        *   `spray_gap`: Khoảng thời gian tính bằng ngày kể từ lần phun thuốc bảo vệ thực vật gần nhất (ví dụ: `7 ngày`).
4.  **Reasoning Agent (Lập luận tích hợp - DeepSeek Engine):**
    *   *Nhiệm vụ:* Hợp nhất dữ liệu từ Vision, Symptom và Context Agent. Sử dụng LLM DeepSeek để phân tích cơ chế gây bệnh, đưa ra chẩn đoán chính xác nhất, giải thích nguyên nhân (`why`), đề xuất giải pháp IPM sinh học và thiết lập ngưỡng gọi chuyên gia thực địa.
5.  **Safety Agent (Kiểm soát an toàn & IPM):**
    *   *Nhiệm vụ:* Chốt chặn an toàn sinh học, cảnh báo chống lạm dụng thuốc bảo vệ thực vật hóa học độc hại.
    *   *Tham số đầu ra:*
        *   `ipm_first`: Ưu tiên các biện pháp vật lý/sinh học trước (`true/false`).
        *   `chemical_advice`: Khuyến nghị sử dụng thuốc hóa học (`deferred` - hoãn lại, hoặc `approved` - cho phép kèm điều kiện).
        *   `expert_needed`: Có cần sự can thiệp trực tiếp của chuyên gia bảo vệ thực vật không (`true/false`).
6.  **Diary Agent (Ghi chép & Nhắc lịch tự động):**
    *   *Nhiệm vụ:* Tự động đăng ký sự kiện bệnh lý vào Nhật ký mùa vụ và thiết lập lịch nhắc nhở theo dõi sau 48h.
    *   *Tham số đầu ra:*
        *   `case_saved`: Đã lưu trữ bệnh án thành công vào MongoDB (`true/false`).
        *   `reminder`: Thiết lập lịch nhắc chụp lại ảnh (mặc định sau `48h`).
        *   `farm_log`: Tạo bản ghi nhật ký phun xịt/can thiệp tự động (`created`).

---

### 💻 2. Các Phân Hệ & Giao Diện Hiện Có (Functional Dashboards)

1.  **Bàn chẩn đoán lâm sàng (`/diagnosis/new`):**
    *   Khung kéo thả tải ảnh thông minh, trích xuất chính xác **tên file ảnh gốc** của tệp tải lên.
    *   Bộ công cụ phóng to/thu nhỏ ảnh để soi kỹ các đốm nấm nứt quả.
    *   Bảng tiến độ hiển thị trực quan sơ đồ 6 Agent chạy theo thời gian thực kèm thông số telemetry động của từng bước.
2.  **Lịch sử bệnh án (`/diagnosis/history`):**
    *   Danh sách 100% ca bệnh thật được tải động từ MongoDB backend.
    *   Nút xem chi tiết (`ri-eye-line`) hiển thị popup chứa ảnh gốc và **đầy đủ lịch sử audit log (trace log) chi tiết của 6 Agent** của riêng ca bệnh đó.
3.  **Hàng đợi ca cần theo dõi (`/diagnosis/follow-up`):**
    *   Hiển thị danh sách các ca bệnh chờ bổ sung triệu chứng từ nông dân, các ca bệnh nguy cơ cao chờ chuyên gia phê duyệt và các lịch nhắc chụp lại ảnh theo dõi sau 48h.
4.  **Bản đồ dịch bệnh hợp tác xã (`/cooperative/map`):**
    *   Vẽ bản đồ tọa độ phân bố ca dịch hại theo khu vực (Trảng Bom, Long Thành, Nhơn Trạch...). Số liệu trên từng huyện được gom nhóm tự động từ các ca bệnh thực tế trong database.
    *   Bảng tin "Cảnh báo gần đây" hiển thị dòng cảnh báo dịch bệnh mới nhất theo thời gian thực.
5.  **Quản lý vườn & Nhật ký mùa vụ (`/farms` & `/farm-logs`):**
    *   Theo dõi chỉ số sức khỏe của từng vườn cây (tỷ lệ hại lá, độ ẩm đất, nhiệt độ).
    *   Nhật ký dòng thời gian (timeline) ghi chép lịch tưới tiêu, bón phân NPK và lịch sử can thiệp dịch bệnh thật.
6.  **Nhật ký kiểm toán AI (`/ai/agent-logs`):**
    *   Trang chuyên dụng cho kỹ sư hệ thống kiểm tra chi tiết input/output, thời gian chạy (latency) và các bằng chứng thực nghiệm (evidence) của từng Agent. Hỗ trợ tự động định vị trace của ca bệnh khi bấm chuyển từ danh sách lịch sử.
7.  **AI-Native Operations Copilot (`/ai-copilot`):**
    *   Bàn điều khiển hoạt động thông minh hỗ trợ vận hành nông trại. Tích hợp chấm điểm rủi ro qua mô hình học sâu PyTorch và hàng đợi duyệt Human-in-the-Loop.

---

## 🚀 PHẦN 2: LỘ TRÌNH NÂNG CẤP & MỞ RỘNG (ROADMAP)

Dưới đây là chi tiết 12 hạng mục nâng cấp hệ thống liên kết chéo và CRUD nhằm nâng cao tối đa trải nghiệm người dùng:

### 🔄 1. Chẩn Đoán Lại & Dùng Ca Cũ Làm Mẫu
*   **Chẩn đoán ảnh mới:** Thêm nút "Chẩn đoán ảnh mới" ở cuối trang chẩn đoán để reset sạch form mà không cần reload trang.
*   **Tải mẫu chẩn đoán cũ:** Trong Modal chi tiết ca bệnh ở trang Lịch sử, thêm nút **"Dùng làm mẫu chẩn đoán lại"**. Khi bấm, hệ thống chuyển hướng sang trang Chẩn đoán mới và tự động điền sẵn (pre-fill) ảnh cũ, cây trồng cũ và triệu chứng cũ, nông dân chỉ việc chỉnh sửa bối cảnh rồi chạy lại chẩn đoán.

### 🎨 2. Chuẩn Hóa Nhãn Giao Diện (Bootstrap 5 Badge)
*   Chuyển các nhãn kiểu cũ `badge-pill` và các thẻ `bg-danger` chói mắt sang định dạng capsule mềm mại chuẩn Velzon: `rounded-pill bg-danger` và các badge phối màu dịu `bg-danger-subtle text-danger`, `bg-warning-subtle text-warning`, `bg-success-subtle text-success`.

### 🗑️ 3. Quản Trị Ca Bệnh (CRUD Lịch Sử)
*   **Xóa ca bệnh:** Thêm nút thùng rác đỏ ở mỗi dòng trong trang Lịch sử chẩn đoán. Khi bấm, mở Modal xác nhận và gọi API `DELETE /api/diagnosis/cases/{case_id}` để xóa sạch ca lỗi.
*   **Sửa ghi chú điều trị:** Cho phép chỉnh sửa trường khuyến cáo hoặc ghi chú điều trị của ca bệnh ngay trong Modal chi tiết của trang Lịch sử (gửi `PATCH /api/diagnosis/cases/{case_id}` để cập nhật thực tế điều trị của nông trại).

### 🤖 4. Tương Tác Trực Quan Trong Luồng Chạy AI
*   **Tooltip Agent:** Cho phép người dùng click/hover vào biểu tượng Agent ở sơ đồ Bước 2 để hiển thị nhanh mô tả nhiệm vụ của Agent đó (ví dụ: *"Context Agent đang đọc thông số khí tượng tại Trảng Bom"*).
*   **Popup Tri Thức Nhanh:** Tại trang kết quả chẩn đoán, khi click vào tên bệnh (ví dụ: *Thán thư*), hệ thống sẽ mở một popup hiển thị nhanh các biện pháp phòng trừ sinh học/hóa học IPM lấy từ Thư viện bệnh cây mà không bắt nông dân đổi trang.

### 🔗 5. Liên Kết Chéo & Tương Tác Giữa Các Phân Hệ
*   **Bản đồ ➔ Bệnh án:** Click vào mã ca bệnh trên Bản đồ dịch bệnh hoặc bảng tin cảnh báo sẽ chuyển hướng sang trang Lịch sử và tự động mở Modal chi tiết ca bệnh đó.
*   **Bộ lọc bản đồ:** Thêm dropdown lọc nhanh bản đồ theo loại cây trồng (Ớt, Cà chua, Dưa leo).
*   **Quản lý vườn (CRUD Farms):** Bổ sung nút **"Thêm vườn mới"** (nhập tên, vị trí, diện tích, cây trồng và gửi `POST /api/farms`) và nút xóa vườn ngay trên giao diện `/farms`.
*   **Nhật ký mùa vụ thủ công:** Thêm nút **"Tạo nhật ký mới"** tại trang `/farm-logs`, cho phép nông dân chọn vườn, loại tác vụ (Tưới nước, Bón phân NPK, làm cỏ...) và viết ghi chú lưu thẳng xuống database.
*   **Lịch nhắc hoàn thành:** Tích chọn checkbox hoàn thành lịch nhắc tại trang `/reminders` sẽ gửi API `PATCH /api/reminders/{reminder_id}` cập nhật trạng thái vĩnh viễn vào MongoDB.
*   **Shortcut chụp ảnh:** Lịch nhắc loại `"camera"` (Chụp lại ảnh theo dõi) sẽ có nút shortcut dẫn thẳng sang trang Chẩn đoán mới và tự động điền sẵn tên vườn cần chụp.

### 🛡️ 6. Cơ Chế Thuyết Trình An Toàn & Triển Khai
*   **Offline Demo Mode Switch:** Thêm một công tắc trong Cài đặt hệ thống. Khi bật, hệ thống sẽ sử dụng RAG cục bộ và mô phỏng lập luận phản hồi tức thì (< 100ms) mà không gọi API DeepSeek qua mạng, bảo vệ buổi thuyết trình live demo tránh 100% rủi ro nghẽn mạng trên sân khấu.
*   **Dockerization:** Viết file `docker-compose.yml` tích hợp sẵn ở thư mục gốc của dự án để khởi chạy FastAPI, Next.js và MongoDB chỉ với một lệnh: `docker-compose up --build`.
*   **Grad-CAM tương tác:** Cho phép tải ảnh lên trang `/ai/model-report` để xem bản đồ nhiệt phân bố đặc trưng mạng nơ-ron học sâu PyTorch.
