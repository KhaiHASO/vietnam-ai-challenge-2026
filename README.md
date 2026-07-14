# Canopy — Nền tảng AI-Native Copilot & CropDoctor

Canopy là nền tảng AI-Native hỗ trợ chẩn đoán cây trồng và tư vấn chuyên môn có kiểm soát. Hệ thống kết hợp Web UI, API, worker bất đồng bộ và `ai_layer/rag` (RAG, memory, cache, registry, validation, policy và typed abstention).

> Khuyến nghị dùng Docker Compose khi demo hoặc vận hành đầy đủ. Cách này chạy đúng topology production: Nginx, Frontend, Backend, Worker, MongoDB, Redis và Chroma.

## Kiến trúc

```text
Trình duyệt
    │
    ▼
Nginx (cổng 80) ──► Frontend Next.js
    │ /api
    ▼
Backend FastAPI ──► ai_layer/rag ──► FPT AI Factory / model provider
    │                    │
    │                    ├── Chroma (vector store)
    │                    └── Redis (cache, queue, rate-limit)
    ▼
MongoDB (người dùng, hội thoại, audit, dữ liệu nghiệp vụ)
    │
    ▼
Worker (ingestion, embedding, tác vụ nền)
```

## Yêu cầu

- Docker Desktop và Docker Compose v2 — cách chạy khuyến nghị.
- Hoặc để phát triển cục bộ: Python 3.11+, Node.js 20+ và npm 10+.
- API key của FPT AI Factory nếu muốn gọi mô hình thật.

## Chạy nhanh với Docker Compose

### 1. Tạo cấu hình môi trường

```powershell
Copy-Item .env.example .env
```

Mở `.env` và thay tối thiểu các giá trị sau:

```dotenv
ENVIRONMENT=production
PUBLIC_ORIGIN=http://localhost
JWT_SECRET=thay-bang-chuoi-ngau-nhien-toi-thieu-32-ky-tu
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=mat-khau-rieng-toi-thieu-12-ky-tu
MONGO_ROOT_PASSWORD=mat-khau-mongodb-manh

# Bắt buộc nếu dùng model FPT AI Factory thật
FPT_AI_FACTORY_API_KEY=
FPT_AI_FACTORY_ENDPOINT=https://api.fpt.ai/v1/chat/completions
FPT_AI_FACTORY_MODEL_ID=qwen2.5-72b-instruct
```

Không commit file `.env` hoặc bất kỳ API key nào vào Git.

### 2. Khởi động toàn bộ hệ thống

```powershell
docker compose up --build -d
docker compose ps
```

Mở ứng dụng tại [http://localhost](http://localhost). Health check: [http://localhost/health/live](http://localhost/health/live).

Tài khoản quản trị đầu tiên được tạo từ `BOOTSTRAP_ADMIN_USERNAME`, `BOOTSTRAP_ADMIN_PASSWORD` và `BOOTSTRAP_ADMIN_TENANT_ID` khi Backend khởi động.

### 3. Xem log hoặc dừng hệ thống

```powershell
docker compose logs -f backend
docker compose logs -f worker
docker compose down
```

`docker compose down -v` sẽ xóa cả dữ liệu MongoDB, Redis và Chroma. Chỉ dùng khi bạn chắc chắn không cần dữ liệu hiện tại.

## Chạy cục bộ để phát triển

### Backend

```powershell
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# Tạo file .env từ .env.example trước khi chạy
$env:PYTHONPATH = "$PWD;$PWD\backend"
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

API khả dụng tại [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) và health check tại `http://127.0.0.1:8000/health/live`.

Để chạy ở chế độ phát triển độc lập, dùng các biến môi trường phù hợp trong `.env`:

```dotenv
ENVIRONMENT=development
DEMO_MODE=true
CORS_ORIGINS=http://localhost:3000
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=cropdoctor_ai
REDIS_URL=redis://localhost:6379/0
CHROMA_URL=http://localhost:8000
PRIMARY_AI_PROVIDER=fpt-ai-factory
FPT_AI_FACTORY_API_KEY=
```

Bạn vẫn cần MongoDB, Redis và Chroma đang chạy nếu muốn kiểm tra đầy đủ RAG, cache, memory và tác vụ ingestion.

### Worker

Mở terminal thứ hai, kích hoạt lại virtual environment rồi chạy:

```powershell
$env:PYTHONPATH = "$PWD;$PWD\backend"
python -m app.workers.main
```

Worker xử lý ingestion tài liệu, embedding và các tác vụ bất đồng bộ. Không bỏ qua worker khi kiểm thử Knowledge Base/RAG.

### Frontend

```powershell
Set-Location frontend
npm ci --legacy-peer-deps
npm run dev
```

UI phát triển mở tại [http://localhost:3000](http://localhost:3000). Lưu ý: các luồng đăng nhập và AI Copilot gọi API cùng origin `/api`; vì vậy Docker Compose (qua Nginx) là cách phù hợp để kiểm thử end-to-end. Khi chạy Next.js độc lập, dùng API docs hoặc cấu hình proxy/rewrite cục bộ nếu cần gọi Backend từ UI.

## Đăng nhập và phân quyền

- `admin`: quản trị tenant, người dùng, Domain Pack và Knowledge Base.
- `expert`: quản lý tri thức và hỗ trợ chuyên môn.
- `operator`: sử dụng các tính năng được cấp quyền.

API xác thực chính:

```text
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

## Luồng AI/RAG an toàn

`ai_layer/rag` là module đóng gói lõi AI, không phải một API RAG tách rời. Một yêu cầu Copilot được xử lý theo các lớp:

```text
Input validation → Policy/authorization → Memory & cache
→ Retrieval từ Domain Pack/Knowledge Base → Agent/LLM
→ Claim & citation validation → Output policy
→ Trả lời có nguồn hoặc Typed Abstention
```

Nguyên tắc quan trọng:

- Memory chỉ dùng cho ngữ cảnh hội thoại, không phải bằng chứng chuyên môn.
- Cache key gắn với phiên bản Domain Pack, prompt và policy để tránh trả kết quả cũ sai ngữ cảnh.
- Câu trả lời chuyên môn cần được kiểm tra claim/citation trước khi trả về.
- Khi thiếu dữ liệu, nguồn không đủ tin cậy hoặc có lỗi kiểm định, Backend trả `typed abstention` thay vì suy đoán.

Frontend cần hiển thị trạng thái abstain một cách rõ ràng: lý do, gợi ý người dùng bổ sung thông tin hoặc chuyển sang tư vấn viên/chuyên gia.

## Nạp tri thức cho RAG

1. Đăng nhập bằng tài khoản `admin` hoặc `expert`.
2. Chọn hoặc tạo Domain Pack phù hợp.
3. Gửi tài liệu qua Knowledge Base/Copilot UI hoặc API ingestion.
4. Bảo đảm worker đang chạy để chunking và embedding hoàn tất.
5. Kiểm tra nguồn trích dẫn và kết quả retrieval trước khi bật cho người dùng cuối.

Endpoint ingestion yêu cầu quyền phù hợp:

```text
POST /api/v1/knowledge/ingestions
```

## Kiểm thử và kiểm tra chất lượng

### Backend và AI layer

```powershell
$env:PYTHONPATH = "$PWD;$PWD\backend"
python -m pytest backend/tests tests -q
```

### Frontend

```powershell
Set-Location frontend
npm run test
npm run type-check
npm run lint
npm run format:check
```

### Release/operational checks

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_release.ps1
```

Build frontend có thể mất thời gian vì dự án vẫn chứa một số route/template kế thừa. Không nên coi một lần build timeout là đạt tiêu chuẩn release; hãy kiểm tra log, tài nguyên Docker và chạy lại trong môi trường CI trước khi phát hành.

## Sao lưu và khôi phục

```powershell
powershell -ExecutionPolicy Bypass -File scripts/backup.ps1
powershell -ExecutionPolicy Bypass -File scripts/restore_verify.ps1 -BackupDirectory <thu_muc_backup>
```

Thực hiện khôi phục thử định kỳ; backup không được xem là hợp lệ nếu chưa khôi phục và kiểm tra được.

## Mở rộng sang domain mới

Core hiện tại được thiết kế để tái sử dụng khi đổi chủ đề cuộc thi. Khi nhận domain mới, không cần viết lại AI layer; hãy:

1. Tạo Domain Pack mới: taxonomy, prompt, policy, tool/registry và tiêu chí citation.
2. Nạp tài liệu tri thức đáng tin cậy, version hóa nguồn và chạy ingestion.
3. Cấu hình validator/policy theo mức rủi ro của domain.
4. Viết bộ evaluation gồm câu đúng, câu thiếu thông tin, prompt injection và trường hợp phải abstain.
5. Kiểm thử end-to-end trước khi bật domain mới cho người dùng.

Với domain có rủi ro cao (y tế, pháp lý, tài chính), bắt buộc bổ sung policy, quy trình escalation người thật và review chuyên gia phù hợp; RAG không tự động bảo đảm tính đúng đắn.

## Tài liệu liên quan

- [Kế hoạch triển khai AI-Native](docs/superpowers/plans/2026-07-10-ai-native-production-implementation.md)
- [Runbook vận hành](docs/operations/runbook.md)
- [Hướng dẫn đổi Domain Pack](docs/architecture/domain-pack-migration-guide.md)
- [Ma trận production readiness](docs/architecture/production-readiness-matrix.md)

## Khắc phục lỗi thường gặp

| Hiện tượng | Kiểm tra trước |
| --- | --- |
| Không đăng nhập được | Kiểm tra `BOOTSTRAP_ADMIN_*`, `JWT_SECRET`, log Backend và truy cập qua Nginx (`http://localhost`). |
| Copilot trả abstain | Kiểm tra Domain Pack đang hoạt động, nguồn Knowledge Base, trạng thái worker và citation/retrieval trong audit/log. |
| Nạp tài liệu xong chưa tìm thấy | Worker chưa chạy, Redis/Chroma không kết nối được hoặc ingestion đang lỗi. Xem log worker. |
| FPT AI Factory lỗi | Kiểm tra `FPT_AI_FACTORY_API_KEY`, endpoint, model ID, quota và log provider; không đưa key vào log. |
| Frontend ở cổng 3000 không gọi được API | Đây là giới hạn chạy dev độc lập; dùng Docker Compose/Nginx hoặc thiết lập proxy/rewrite cục bộ. |

## Lưu ý bảo mật

- Dùng secret ngẫu nhiên, mạnh và khác nhau cho JWT, MongoDB và tài khoản bootstrap.
- Chỉ expose Nginx ra internet; MongoDB, Redis, Chroma, Backend và Worker nên ở mạng nội bộ.
- Thiết lập HTTPS, origin thật trong `PUBLIC_ORIGIN`, rate-limit, backup và observability trước khi public.
- Không xem AI output là nguồn chuyên môn tuyệt đối; luôn bảo toàn citation, policy và cơ chế abstain.
