# AI Workspace: Knowledge Base and Operations

## Mục tiêu

Biến Focus Canvas thành điểm vào cho một không gian AI-native hoàn chỉnh. Người có
quyền phải có thể nạp tri thức, biết tài liệu đã được index hay chưa và quay về
Copilot để truy vấn cùng domain; vận hành viên phải quan sát được các trạng thái
an toàn mà không biến giao diện Copilot thành dashboard nặng nề.

## Phạm vi

- Giữ app shell, cách bố trí responsive, bảng, badge và modal của template Velzon
  hiện tại.
- Giữ visual language của Focus Canvas cho bề mặt AI: nền sáng, xanh rêu,
  typography gọn, evidence và assurance là các đối tượng hạng nhất.
- Thêm điều hướng thống nhất giữa AI Copilot, Knowledge Base và AI Operations.
- Thêm API trạng thái ingestion được giới hạn theo tenant để UI không phải đoán
  việc index có hoàn tất hay không.
- Gửi `domain_id` đang chọn cùng mỗi truy vấn Copilot, chỉ hiển thị domain pack
  đã tồn tại trong runtime hiện tại.

## Không thuộc phạm vi

- Xây dựng lại toàn bộ template hoặc di trú tất cả trang legacy sang Tailwind.
- Tạo danh mục tài liệu/chunk bền vững khi backend chưa lưu metadata document.
- Hiển thị dữ liệu observability giả hoặc cho phép thao tác xoá/retry job từ UI.
- Nhận PDF/DOCX/XLSX ở UI trước khi pipeline trích xuất nhị phân được xác thực.
  Màn upload giai đoạn này chỉ nhận TXT/CSV.

## Điều hướng và màn hình

### AI Copilot (`/ai-copilot`)

- Focus Canvas là bề mặt hỏi đáp chính, có liên kết rõ sang Knowledge Base.
- Domain selector chỉ chứa `agriculture`, vì đây là domain pack có manifest và
  index tại thời điểm triển khai.
- `domain_id` được gửi trong payload streaming để retrieval bám đúng tri thức.
- Panel nguồn tiếp tục là nơi hiển thị citation; khi chưa có nguồn, empty-state
  hướng người dùng nạp tri thức hoặc đặt một truy vấn có kiểm chứng.

### Knowledge Base (`/knowledge`)

- Một màn làm việc chính, không phải card gallery: vùng upload ở trung tâm, một
  panel bên cạnh mô tả domain, quyền truy cập và trạng thái index.
- Chỉ Admin/Expert được chọn tệp và gửi upload; người chưa đăng nhập hoặc không
  đúng vai trò thấy giải thích và nút quay về Copilot, không thấy một nút hỏng.
- Sau khi upload, UI giữ `job_id`, poll endpoint trạng thái và mô tả rõ `queued`,
  `running`, `completed`, `failed/dead_letter`.
- Trạng thái hoàn tất có CTA quay lại Copilot; lỗi có thông báo an toàn, không
  tiết lộ path hay chi tiết nội bộ.

### Knowledge job (`/knowledge/[jobId]`)

- URL có thể chia sẻ trong cùng tenant; trang đọc trạng thái ingestion bằng API
  đã kiểm soát quyền.
- Hiển thị id rút gọn, trạng thái, số lần thử và thông báo người dùng; không
  render stack trace hoặc payload lưu trữ.

### AI Operations (`/ai-operations`)

- Màn read-only để demo trạng thái thành phần AI: assurance, memory/cache rule,
  typed abstention và pipeline health.
- Chỉ trình bày trạng thái có thể chứng minh từ endpoint hiện có; nếu endpoint
  chưa tồn tại, dùng empty-state minh bạch thay vì số liệu mô phỏng.

## Backend và an toàn

- `POST /api/v1/knowledge/ingestions` vẫn nhận file multipart và kiểm tra role
  `ADMIN`/`EXPERT`.
- Thêm `GET /api/v1/knowledge/ingestions/{job_id}`. Endpoint truy vấn job theo
  `job_id` *và tenant_id* của principal; trả 404 khi job không cùng tenant.
- Response chỉ gồm `job_id`, `status`, `attempts`, `last_error` đã làm sạch và
  metadata hiển thị được. Không trả storage key, payload gốc hoặc tenant của
  người khác.
- Frontend dùng `authorizedFetch`; multipart không tự đặt `Content-Type` để
  browser tạo boundary đúng.

## Trạng thái và lỗi

- File bị thiếu/sai định dạng: chặn ngay ở client, thông báo định dạng TXT/CSV.
- Upload 401/403: thông báo cần đăng nhập hoặc quyền chuyên gia, không retry.
- Upload/network lỗi: giữ file đã chọn để người dùng có thể thử lại.
- Job pending/running: polling nhẹ, có nút cập nhật thủ công.
- Job failed/dead letter: dừng polling, trình bày recovery action chung.
- Job completed: dừng polling, CTA "Mở AI Copilot" giữ domain hiện tại.

## Kiểm thử và tiêu chí chấp nhận

- Unit test frontend kiểm tra payload multipart gồm file/domain và không gắn
  header Content-Type thủ công.
- Component test kiểm tra trạng thái role, upload thành công, pending và CTA.
- Backend route test kiểm tra Admin/Expert đọc được job cùng tenant và không đọc
  được job tenant khác.
- Copilot API test kiểm tra `domain_id` được gửi.
- Type-check, targeted Vitest, targeted pytest route test và `git diff --check`
  phải được chạy trước khi báo hoàn tất. Khi Docker daemon/browser không sẵn
  sàng, ghi rõ giới hạn thay vì tuyên bố smoke test E2E đã qua.

## Quyết định

Ưu tiên hoàn thiện luồng upload-to-answer có bằng chứng hơn là các dashboard số
liệu. Đây là phần nhìn thấy rõ nhất cho demo AI-native và tránh đánh lừa người
dùng về trạng thái RAG.
