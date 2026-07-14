## Why

Nền tảng hiện tại đã có khung AI-native dùng lại được (Next.js, FastAPI, RAG có memory/cache/validation, PyTorch, MongoDB, Redis, Chroma và Docker Compose) nhưng đang khóa vào domain nông nghiệp và chưa có learner model, curriculum graph, kiểm chứng toán học hay trải nghiệm giáo viên/học sinh theo đề MathPath THPT. Thay đổi này chuyển nền tảng thành một sản phẩm giáo dục có thể demo, đo lường và pilot, thay vì dựng một chatbot Toán tách rời hoặc một mockup không có AI thật phía sau.

## What Changes

- Thêm Domain Pack `education-mathpath` bám Chương trình GDPT 2018, taxonomy kiến thức Toán THPT, chính sách gợi mở, policy bảo vệ người chưa thành niên và bộ đánh giá riêng.
- Thêm curriculum knowledge graph tối thiểu 40 nút cho hai mạch Đại số và Giải tích, cùng quan hệ tiên quyết, chuẩn đầu ra, misconception và liên kết học liệu/bài tập.
- Thêm trải nghiệm học sinh responsive để làm bài theo từng bước, hỏi đáp nhiều lượt, nhận gợi ý tăng dần, xem bằng chứng kiểm chứng và lộ trình cá nhân.
- Thêm learner state cập nhật sau mỗi attempt, nhận diện lỗ hổng/misconception, ước lượng mastery có confidence và chọn bài tiếp theo theo chính sách sư phạm.
- Thêm Math Verification Layer dùng SymPy/rule engine để chuẩn hóa biểu thức, kiểm tra tương đương, nghiệm, đạo hàm và phát hiện bước biến đổi mâu thuẫn trước khi phát hành phản hồi.
- Thêm workspace giáo viên với heatmap theo lớp/chủ đề, danh sách cần hỗ trợ, lỗi phổ biến, bằng chứng và quy trình duyệt/chỉnh/giao can thiệp.
- Mở rộng orchestrator thành vòng lặp quan sát → chẩn đoán → lập kế hoạch → gợi mở/tool call → kiểm chứng → cập nhật learner state; không stream chain-of-thought và không tự động ra quyết định điểm/xếp loại.
- Thêm adapter LMS Sandbox cho ít nhất ba endpoint bắt buộc, cơ chế idempotency/retry/audit và đồng bộ recommendation/teacher note sau phê duyệt.
- Thay model hard-code bằng capability-based model routing và benchmark gate; dùng LLM mạnh cho hội thoại/lập kế hoạch, PyTorch cho tín hiệu mastery/misconception/risk, retrieval cho căn cứ và math tool cho tính đúng.
- Thêm dữ liệu synthetic tối thiểu 30 học sinh, lịch sử attempt và năm hành trình demo; thêm golden sets để đo F1 chẩn đoán, độ đúng toán, chất lượng gợi mở, retrieval/citation, latency, cost và privacy.
- Cập nhật deployment, seed, runbook, README và kịch bản demo để chạy được bằng Docker Compose, có fallback khi provider/LMS lỗi và có live URL trước ngày trình bày.

## Capabilities

### New Capabilities

- `mathpath-domain-pack`: Curriculum graph, nguồn tri thức, prompt/policy/validator bundle và quy trình ingestion của Toán THPT.
- `student-learning-experience`: Luồng làm bài, hội thoại gia sư, gợi ý tăng dần, phản hồi từng bước và lộ trình cá nhân cho học sinh.
- `learner-modeling-personalization`: Learner state, mastery, misconception, knowledge tracing và lựa chọn bài luyện tiếp theo.
- `verified-math-tutoring`: Math tool, kiểm chứng phép biến đổi/kết quả, confidence và cơ chế từ chối khi không thể xác minh.
- `teacher-intervention-workspace`: Heatmap lớp học, cảnh báo có căn cứ, lỗi phổ biến và quy trình giáo viên duyệt can thiệp.
- `lms-sandbox-integration`: Đồng bộ học sinh, attempt, skill, assignment và recommendation/teacher note qua LMS Sandbox.
- `education-ai-orchestration-safety`: Orchestration nhiều lượt, scoped memory, RAG/tool calling, guardrail, privacy, HITL và trace cho người học chưa thành niên.
- `mathpath-model-evaluation`: Model routing, PyTorch engine, benchmark/golden set và release gates định lượng cho MathPath.
- `mathpath-demo-deployment`: Dữ liệu mô phỏng, demo journeys, quan sát vận hành, Docker/live deployment và tài liệu bàn giao.

### Modified Capabilities

Không có. Kho `openspec/specs/` chưa có capability baseline; các capability trên mở rộng code hiện hữu nhưng được đặc tả mới trong change này.

## Impact

- **Frontend:** thay shell và route nông nghiệp bằng navigation theo vai trò; thêm student practice/tutor/path và teacher dashboard/intervention; tái sử dụng auth, Focus Canvas, SSE reducer, evidence/approval/degraded states và design system hiện có.
- **Backend:** thêm module education, curriculum, learning, math verification và LMS; mở rộng RBAC từ `admin/expert/operator` sang mapping `admin/teacher/student`; bổ sung collections/indexes cho graph, attempts, learner states, assignments, interventions và audit.
- **AI layer:** thêm domain manifest/prompt/policy/evaluation, graph-aware retrieval, tutoring graph, SymPy tools, mastery/misconception model và provider benchmark registry; loại bỏ prompt nông nghiệp hard-code khỏi FPT adapter.
- **Data:** tạo seed synthetic, source registry và pipeline chuẩn hóa/chunk theo `grade/strand/topic/skill/outcome/version`; không dùng dữ liệu học sinh thật trong demo.
- **Infrastructure:** giữ topology Nginx + Next.js + FastAPI + worker + MongoDB + Redis + Chroma; không đưa Neo4j/Kubernetes/OCR vào MVP trừ khi core gates đã đạt.
- **External systems:** FPT AI Factory là provider ưu tiên nếu model được chọn vượt benchmark; OpenAI/Gemini là adapter fallback có policy; LMS Sandbox và Math Tool là tích hợp bắt buộc.
