# VAIC 2026 — Checklist lụm Giải Nhất + Best PyTorch Award

> Phiên bản dành cho team FPT Polytechnic Đồng Nai trước D-Day.  
> Mục tiêu: không làm demo AI cho vui, mà làm một **AI-native product prototype** có pain thật, demo rõ, PyTorch thật, đo được tác động, có pilot pathway và đủ sức trả lời giám khảo.

---

## 0. Tư duy chốt trước khi làm

### 0.1. Câu chốt của toàn đội

- [ ] Không đi thi bằng “ý tưởng hay”.
- [ ] Không đi thi bằng “chatbot”.
- [ ] Không đi thi bằng “app CRUD có gắn AI”.
- [ ] Không đi thi bằng “model train cho vui”.
- [ ] Đi thi bằng **một sản phẩm AI-native giải quyết một workflow thật**.
- [ ] Demo phải chứng minh được: **dữ liệu vào → AI xử lý → người duyệt → hành động → đo kết quả**.
- [ ] Nếu bỏ AI ra mà sản phẩm vẫn chạy gần như cũ, tức là chưa đủ AI-native.
- [ ] Nếu bỏ PyTorch ra mà sản phẩm không mất gì, tức là chưa đủ sức tranh PyTorch Award.

### 0.2. Định vị đội

- [ ] Team không chỉ là “coder”.
- [ ] Team phải tự định vị là: **Product Builder + AI Engineer + Storyteller**.
- [ ] Code giúp đội được chú ý.
- [ ] Pilot pathway giúp đội được tin.
- [ ] PyTorch layer giúp đội có cơ hội ăn Best PyTorch Award.
- [ ] Storytelling giúp đội thắng trong phòng chấm.

### 0.3. Công thức thắng

```text
Pain thật
+ Data hợp lý
+ AI nằm đúng chỗ
+ PyTorch đóng vai trò kỹ thuật thật
+ Demo 5–7 phút cực mượt
+ Metric rõ
+ Human-in-the-loop
+ Pilot 2 tuần
+ Pitch sắc
+ Q&A chắc
= Có cửa Giải Nhất + PyTorch Award
```

---

## 1. Mục tiêu kép: Giải Nhất và Best PyTorch Award

## 1.1. Muốn ăn Giải Nhất thì phải chứng minh 5 thứ

- [ ] Hiểu đúng bài toán doanh nghiệp/đơn vị ra đề.
- [ ] Chọn đúng người dùng chính, không ôm toàn bộ tổ chức.
- [ ] Sản phẩm có workflow vận hành thật, không chỉ hỏi đáp.
- [ ] Demo có “wow moment” trong 5–7 phút.
- [ ] Có pilot pathway: thử nhỏ, đo được, có rủi ro kiểm soát.

### Tín hiệu bài có khả năng Giải Nhất

- [ ] Giám khảo hiểu pain trong 30 giây đầu.
- [ ] Giám khảo thấy dữ liệu đầu vào giống thật.
- [ ] Giám khảo thấy AI làm việc mà dashboard thường không làm được.
- [ ] Giám khảo thấy con người vẫn kiểm soát quyết định quan trọng.
- [ ] Giám khảo thấy có số liệu trước/sau.
- [ ] Giám khảo tin sản phẩm có thể pilot sau cuộc thi.
- [ ] Giám khảo không phải tự tưởng tượng giá trị.

## 1.2. Muốn ăn Best PyTorch Award thì phải chứng minh 6 thứ

- [ ] PyTorch không chỉ xuất hiện trong `requirements.txt`.
- [ ] Có một model/pipeline PyTorch thật sự đóng vai trò trong sản phẩm.
- [ ] Có dữ liệu, train/eval/inference rõ ràng.
- [ ] Có metrics: accuracy, F1, recall, latency, throughput hoặc cost.
- [ ] Có optimization/deployment: `torch.compile`, ONNX export, benchmark, model card.
- [ ] Có slide riêng: **Why PyTorch mattered**.

### Tín hiệu PyTorch Award mạnh

- [ ] Có thư mục `ai_layer/pytorch_engine/` sạch, dễ đọc.
- [ ] Có `model.py`, `dataset.py`, `train.py`, `evaluate.py`, `inference.py`, `export_onnx.py`, `benchmark.py`.
- [ ] Có checkpoint hoặc artifact model.
- [ ] Có model card.
- [ ] Có báo cáo benchmark.
- [ ] Có API gọi model thật trong demo.
- [ ] Có UI hiển thị output từ PyTorch model.
- [ ] Có fallback nếu model lỗi.
- [ ] Có giải thích vì sao bài toán cần model nhỏ/chuyên biệt thay vì chỉ LLM.

---

## 2. Quyết định lớn: bỏ “đặt sân” khỏi định vị

Repo hiện tại có thể giữ làm core, nhưng **không được pitch là app đặt sân**.

### 2.1. Cách nói đúng

- [ ] “Đặt sân chỉ là kịch bản test kỹ thuật ban đầu.”
- [ ] “Core của chúng em là AI-native workflow cockpit.”
- [ ] “Khi nhận đề thật, chúng em thay domain pack, data schema, tool nghiệp vụ và policy base.”
- [ ] “Nền tảng này dùng để biến dữ liệu rời rạc thành hành động có kiểm soát.”

### 2.2. Cách sửa README/repo

- [ ] Xóa hoặc giảm nổi bật wording quá hẹp như “booking court”.
- [ ] Đổi positioning thành:

```text
AI-Native Workflow Copilot
A domain-adaptable product skeleton for solving real business workflows with:
RAG + PyTorch risk/triage model + tool execution + human approval + telemetry + pilot metrics.
```

- [ ] Tách use case đặt sân thành `examples/booking_demo/`.
- [ ] Tạo 3 domain pack chính:
  - [ ] `domains/education/`
  - [ ] `domains/agriculture/`
  - [ ] `domains/sme/`
- [ ] Tạo `docs/product_positioning.md`.
- [ ] Tạo `docs/demo_strategy.md`.
- [ ] Tạo `docs/pytorch_award_strategy.md`.

---

## 3. Cấu trúc repo nên có trước ngày thi

```text
vietnam-ai-challenge-2026/
│
├── README.md
├── docker-compose.yml
├── run_project.ps1
├── Makefile
├── .env.example
├── requirements.txt
├── package.json
│
├── frontend/
│   ├── src/
│   └── README.md
│
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── services/
│   ├── schemas/
│   └── tests/
│
├── ai_layer/
│   ├── orchestrator/
│   ├── rag/
│   ├── tools/
│   ├── guardrails/
│   ├── memory/
│   ├── evaluation/
│   └── pytorch_engine/
│       ├── README.md
│       ├── model.py
│       ├── dataset.py
│       ├── train.py
│       ├── evaluate.py
│       ├── inference.py
│       ├── export_onnx.py
│       ├── benchmark.py
│       ├── model_card.md
│       ├── configs/
│       ├── checkpoints/
│       └── results/
│
├── domains/
│   ├── education/
│   │   ├── README.md
│   │   ├── problem_brief.md
│   │   ├── product_canvas.md
│   │   ├── pilot_plan.md
│   │   ├── risk_plan.md
│   │   ├── demo_script.md
│   │   ├── data/
│   │   ├── policies/
│   │   ├── prompts/
│   │   └── eval_cases.json
│   │
│   ├── agriculture/
│   │   ├── README.md
│   │   ├── problem_brief.md
│   │   ├── product_canvas.md
│   │   ├── pilot_plan.md
│   │   ├── risk_plan.md
│   │   ├── demo_script.md
│   │   ├── data/
│   │   ├── policies/
│   │   ├── prompts/
│   │   └── eval_cases.json
│   │
│   └── sme/
│       ├── README.md
│       ├── problem_brief.md
│       ├── product_canvas.md
│       ├── pilot_plan.md
│       ├── risk_plan.md
│       ├── demo_script.md
│       ├── data/
│       ├── policies/
│       ├── prompts/
│       └── eval_cases.json
│
├── docs/
│   ├── 00_competition_strategy.md
│   ├── 01_architecture.md
│   ├── 02_ai_native_workflow.md
│   ├── 03_pytorch_award_strategy.md
│   ├── 04_demo_7_minutes.md
│   ├── 05_judge_qa.md
│   ├── 06_pilot_pathway.md
│   ├── 07_risk_and_guardrails.md
│   ├── 08_evaluation_report.md
│   ├── 09_pitch_deck_outline.md
│   └── 10_day_d_runbook.md
│
├── demo/
│   ├── video_backup.mp4
│   ├── screenshots/
│   ├── sample_inputs.md
│   ├── sample_outputs.md
│   └── fallback_script.md
│
└── scripts/
    ├── seed_domain.py
    ├── switch_domain.py
    ├── run_eval.py
    ├── smoke_test.py
    └── record_demo_checklist.md
```

---

## 4. Checklist README để repo nhìn như đội chuyên nghiệp

## 4.1. README đầu trang

- [ ] Có tên sản phẩm rõ.
- [ ] Có tagline 1 câu.
- [ ] Có ảnh/screenshot UI.
- [ ] Có video demo link hoặc GIF.
- [ ] Có architecture diagram.
- [ ] Có quick start dưới 5 phút.
- [ ] Có phần “Why AI-native?”.
- [ ] Có phần “Why PyTorch?”.
- [ ] Có phần “Human-in-the-loop & Trust”.
- [ ] Có phần “Pilot plan”.
- [ ] Có phần “Evaluation”.
- [ ] Có phần “Team”.

### Tagline gợi ý

```text
An AI-native workflow copilot that turns messy operational data into trusted, human-approved actions.
```

Hoặc tiếng Việt:

```text
Trợ lý vận hành AI-native biến dữ liệu rời rạc thành hành động có kiểm soát.
```

## 4.2. Quick start bắt buộc

- [ ] Clone repo.
- [ ] Copy `.env.example` thành `.env`.
- [ ] Chạy backend.
- [ ] Chạy frontend.
- [ ] Seed domain demo.
- [ ] Chạy PyTorch inference.
- [ ] Mở dashboard.
- [ ] Test 3 câu demo.

Ví dụ:

```bash
git clone <repo-url>
cd vietnam-ai-challenge-2026
cp .env.example .env

make setup
make seed DOMAIN=education
make train-fast DOMAIN=education
make dev
```

## 4.3. README phải trả lời được 5 câu

- [ ] Sản phẩm giải quyết pain gì?
- [ ] Người dùng chính là ai?
- [ ] AI làm phần nào mà hệ thống thường không làm được?
- [ ] PyTorch nằm ở đâu trong workflow?
- [ ] Pilot thế nào sau cuộc thi?

---

## 5. Checklist chọn đề thật trong 60 phút đầu

Khi đề được công bố, **không code ngay**. Team lead phải ép cả đội qua bộ lọc này.

## 5.1. Bảng chọn đề

| Tiêu chí | Câu hỏi | Điểm 1–5 |
|---|---|---|
| Pain | Người dùng đang mất thời gian/tiền/uy tín/chất lượng ở đâu? | |
| AI-fit | Có cần AI thật không hay dashboard/CRUD là đủ? | |
| Data | Có dữ liệu đầu vào mô phỏng hợp lý trong 48h không? | |
| Demo | Có thể demo một luồng sắc trong 7 phút không? | |
| PyTorch-fit | Có chỗ cho model PyTorch đóng vai trò thật không? | |
| Pilot | Có thể pilot 2 tuần với 100–300 mẫu không? | |
| Story | Người nghe không chuyên có hiểu ngay không? | |
| Risk | Có rủi ro để show guardrails/HITL không? | |
| Business value | Có metric trước/sau không? | |
| Feasibility | Team có làm kịp không? | |

- [ ] Chỉ chọn bài đạt tổng từ 38/50 trở lên.
- [ ] Nếu 2 bài ngang nhau, chọn bài có demo rõ hơn.
- [ ] Nếu muốn ăn PyTorch Award, chọn bài có data/model task rõ hơn.
- [ ] Không chọn bài chỉ vì nghe “ngầu”.
- [ ] Không chọn bài cần tích hợp hệ thống thật quá nhiều.
- [ ] Không chọn bài không có dữ liệu mô phỏng đáng tin.

## 5.2. Ba câu hỏi chốt trước khi code

- [ ] Vấn đề có đủ đau không?
- [ ] Vì sao bắt buộc cần AI?
- [ ] Pilot thế nào để doanh nghiệp tin?

Nếu chưa trả lời được 3 câu này, chưa code chính.

---

## 6. Bộ 3 domain pack cần chuẩn bị trước

# 6.1. Domain Pack A — Giáo dục

## 6.1.1. Hướng thắng

```text
AI Student Success Copilot
Phát hiện sớm sinh viên có nguy cơ rớt môn, giải thích nguyên nhân,
gợi ý kế hoạch can thiệp cá nhân hóa và để giảng viên duyệt trước khi gửi.
```

## 6.1.2. Pain

- [ ] Giảng viên không đủ thời gian theo dõi từng sinh viên.
- [ ] Sinh viên yếu thường bị phát hiện quá muộn.
- [ ] Dữ liệu điểm, chuyên cần, bài nộp nằm rời rạc.
- [ ] Cố vấn học tập khó biết ai cần ưu tiên.
- [ ] Sinh viên cần gợi ý học tập chứ không cần đáp án để chép.

## 6.1.3. Data cần có

```text
domains/education/data/
├── students.csv
├── attendance.csv
├── grades.csv
├── assignments.csv
├── lms_activity.csv
├── student_messages.csv
├── intervention_history.csv
└── synthetic_data_readme.md
```

### Cột gợi ý

`students.csv`

- [ ] `student_id`
- [ ] `class_id`
- [ ] `major`
- [ ] `semester`
- [ ] `prior_gpa`
- [ ] `learning_style`
- [ ] `support_note`

`attendance.csv`

- [ ] `student_id`
- [ ] `week`
- [ ] `present`
- [ ] `late`
- [ ] `absent_reason`

`grades.csv`

- [ ] `student_id`
- [ ] `lab_score`
- [ ] `quiz_score`
- [ ] `assignment_score`
- [ ] `midterm_score`
- [ ] `late_submission_count`

`student_messages.csv`

- [ ] `student_id`
- [ ] `message`
- [ ] `timestamp`
- [ ] `channel`

## 6.1.4. PyTorch task cho giáo dục

```text
Student Risk & Intervention Triage Model
Input: điểm + chuyên cần + bài nộp + embedding phản hồi
Output: risk_level, dropout_risk, recommended_intervention_type, confidence
```

- [ ] Model PyTorch dự đoán `risk_level`: low / medium / high.
- [ ] Model PyTorch dự đoán `intervention_type`: nhắc học, gợi ý tài liệu, gặp giảng viên, cố vấn học tập.
- [ ] LLM giải thích và soạn kế hoạch, nhưng PyTorch model tạo tín hiệu dự đoán lõi.
- [ ] UI hiển thị “PyTorch Risk Engine: High risk, confidence 0.84”.
- [ ] HITL: giảng viên duyệt trước khi gửi tin nhắn.

## 6.1.5. Demo 7 phút

- [ ] Upload/seed dữ liệu lớp.
- [ ] Hỏi: “Tuần này sinh viên nào có nguy cơ rớt môn?”
- [ ] PyTorch risk engine xếp hạng 5 sinh viên rủi ro.
- [ ] RAG truy xuất rubric/chính sách môn học.
- [ ] AI giải thích nguyên nhân từng sinh viên.
- [ ] AI đề xuất kế hoạch can thiệp 7 ngày.
- [ ] Giảng viên duyệt/chỉnh tin nhắn.
- [ ] Dashboard hiển thị metric: số sinh viên rủi ro, thời gian tiết kiệm, trạng thái can thiệp.

## 6.1.6. Câu pitch

```text
AI không làm bài thay sinh viên. AI giúp giảng viên phát hiện sớm người học cần hỗ trợ,
đưa ra can thiệp cá nhân hóa và luôn để giảng viên duyệt quyết định cuối cùng.
```

---

# 6.2. Domain Pack B — Nông nghiệp

## 6.2.1. Hướng thắng

```text
CropCare AI Copilot
Hỗ trợ nông dân/chủ vườn phân tích tình trạng cây trồng từ ảnh, nhật ký canh tác,
thời tiết và tri thức nông nghiệp; sau đó tạo kế hoạch chăm sóc có kiểm soát.
```

## 6.2.2. Pain

- [ ] Nông dân phát hiện bệnh/chăm sóc sai thời điểm.
- [ ] Tri thức phân tán: kinh nghiệm cá nhân, hội nhóm, đại lý vật tư, chuyên gia.
- [ ] Khuyến nghị nếu sai có thể gây thiệt hại mùa vụ.
- [ ] Cần lịch hành động, không chỉ cần câu trả lời “cây bị gì”.

## 6.2.3. Data cần có

```text
domains/agriculture/data/
├── farm_profiles.csv
├── crop_logs.csv
├── weather_sample.json
├── pest_disease_cases.csv
├── images/
├── treatment_history.csv
└── synthetic_data_readme.md
```

## 6.2.4. PyTorch task cho nông nghiệp

```text
Plant Symptom Triage Model
Input: ảnh lá/cây + metadata thời tiết/canh tác
Output: symptom_group, severity_level, confidence
```

- [ ] Dùng PyTorch/torchvision train hoặc fine-tune model nhỏ.
- [ ] Nếu không đủ data, dùng model pretrained làm feature extractor + classifier nhỏ.
- [ ] Output không claim “chẩn đoán chắc chắn”.
- [ ] Output là “triage”: nghi ngờ nhóm triệu chứng + mức độ ưu tiên.
- [ ] LLM/RAG tạo kế hoạch chăm sóc dựa trên output + knowledge base.
- [ ] HITL: khuyến nghị hóa chất/thuốc phải cần chuyên gia xác nhận.

## 6.2.5. Demo 7 phút

- [ ] Upload ảnh lá/cây hoặc chọn ảnh mẫu.
- [ ] PyTorch model phân loại triệu chứng/mức độ.
- [ ] RAG truy xuất tri thức chăm sóc.
- [ ] AI hỏi thêm 2–3 câu nếu thiếu dữ kiện.
- [ ] AI tạo kế hoạch 7 ngày.
- [ ] Nếu severity cao, tạo action “gửi chuyên gia duyệt”.
- [ ] Dashboard hiển thị nhật ký theo dõi.

## 6.2.6. Câu pitch

```text
AI không chỉ nói cây bị gì. AI biến dấu hiệu ban đầu thành kế hoạch chăm sóc,
nhật ký theo dõi và cơ chế chuyển chuyên gia khi rủi ro cao.
```

---

# 6.3. Domain Pack C — SME

## 6.3.1. Hướng thắng

```text
SME Operations Copilot
Đọc dữ liệu bán hàng, tồn kho, phản hồi khách, ticket và chính sách nội bộ;
sau đó phát hiện vấn đề, ưu tiên xử lý và đề xuất hành động cho chủ doanh nghiệp.
```

## 6.3.2. Pain

- [ ] Chủ SME có dữ liệu nhưng nằm rời rạc trong Excel, Zalo, inbox, hóa đơn.
- [ ] Không có đội vận hành/BI chuyên nghiệp.
- [ ] Phản hồi khách bị bỏ sót.
- [ ] Tồn kho, khiếu nại, hoàn tiền, nhân sự, doanh thu cần được ưu tiên xử lý hằng ngày.
- [ ] Chủ doanh nghiệp cần “hôm nay xử lý gì trước”, không cần thêm dashboard rối.

## 6.3.3. Data cần có

```text
domains/sme/data/
├── orders.csv
├── inventory.csv
├── customer_messages.csv
├── tickets.csv
├── refunds.csv
├── staff_schedule.csv
├── daily_revenue.csv
└── synthetic_data_readme.md
```

## 6.3.4. PyTorch task cho SME

```text
Customer Issue Priority Model
Input: message text embedding + order value + customer history + SLA info
Output: issue_type, priority_level, escalation_required, confidence
```

- [ ] PyTorch model phân loại intent/priority/risk.
- [ ] LLM tạo phản hồi và action plan.
- [ ] Tool executor tạo ticket/task/report.
- [ ] HITL cho hoàn tiền, giảm giá, hủy đơn, khiếu nại nghiêm trọng.
- [ ] UI show “AI đề xuất — Chủ doanh nghiệp duyệt”.

## 6.3.5. Demo 7 phút

- [ ] Seed dữ liệu bán hàng + feedback khách.
- [ ] Hỏi: “Hôm nay có vấn đề gì cần xử lý trước?”
- [ ] PyTorch model ưu tiên ticket rủi ro.
- [ ] RAG truy xuất chính sách SLA/refund.
- [ ] AI tạo danh sách 5 hành động ưu tiên.
- [ ] Người dùng duyệt một hành động.
- [ ] Hệ thống tạo task/ticket/tin nhắn.
- [ ] Dashboard hiển thị thời gian tiết kiệm và ticket ưu tiên.

## 6.3.6. Câu pitch

```text
SME không thiếu dữ liệu. Họ thiếu một trợ lý vận hành biết gom dữ liệu,
hiểu chính sách, ưu tiên vấn đề và đề xuất hành động có kiểm soát.
```

---

## 7. PyTorch Award — chiến lược kỹ thuật chi tiết

## 7.1. Tên layer nên dùng

```text
PyTorch Impact Triage Engine
```

Hoặc:

```text
PyTorch Risk & Priority Engine
```

Lý do: tên này dùng được cho cả giáo dục, nông nghiệp, SME.

## 7.2. Vai trò trong kiến trúc

```text
Raw Data
→ Feature Builder
→ PyTorch Impact Triage Engine
→ Risk/Priority/Severity Prediction
→ RAG Grounding
→ LLM Planner
→ Tool Action
→ Human Approval
→ Telemetry/Evaluation
```

## 7.3. Không để LLM làm hết

- [ ] LLM không nên tự quyết định rủi ro.
- [ ] LLM không nên tự tính priority.
- [ ] LLM không nên tự nói “high risk” nếu không có model/logic/evidence.
- [ ] PyTorch model tạo tín hiệu định lượng.
- [ ] LLM giải thích, tổng hợp, viết kế hoạch.
- [ ] RAG cung cấp căn cứ.
- [ ] Human duyệt hành động rủi ro.

## 7.4. Thư mục PyTorch bắt buộc

```text
ai_layer/pytorch_engine/
├── README.md
├── model.py
├── dataset.py
├── features.py
├── train.py
├── evaluate.py
├── inference.py
├── export_onnx.py
├── benchmark.py
├── explain.py
├── configs/
│   ├── education.yaml
│   ├── agriculture.yaml
│   └── sme.yaml
├── checkpoints/
├── results/
│   ├── metrics.json
│   ├── confusion_matrix.png
│   ├── latency_benchmark.json
│   └── sample_predictions.json
└── model_card.md
```

## 7.5. `model.py` cần có gì

- [ ] `class ImpactTriageNet(torch.nn.Module)`.
- [ ] Có input tabular features.
- [ ] Có input text/image embedding tùy domain.
- [ ] Có fusion layer.
- [ ] Có multi-head output:
  - [ ] `risk_level`
  - [ ] `priority`
  - [ ] `needs_human_review`
  - [ ] `confidence`
- [ ] Có dropout/batchnorm hợp lý.
- [ ] Có config-driven architecture.

## 7.6. `dataset.py` cần có gì

- [ ] Load CSV/JSON từ domain pack.
- [ ] Validate schema.
- [ ] Split train/val/test.
- [ ] Handle missing values.
- [ ] Normalize numeric features.
- [ ] Encode categorical features.
- [ ] Return PyTorch tensors.
- [ ] Có seed để reproducible.

## 7.7. `train.py` cần có gì

- [ ] CLI argument: `--domain education|agriculture|sme`.
- [ ] Set seed.
- [ ] Load config.
- [ ] Train loop rõ ràng.
- [ ] Save best checkpoint.
- [ ] Log loss/metrics.
- [ ] Early stopping.
- [ ] Mixed precision nếu có GPU.
- [ ] Output `results/train_summary.json`.

## 7.8. `evaluate.py` cần có gì

- [ ] Accuracy.
- [ ] Precision.
- [ ] Recall.
- [ ] F1.
- [ ] Confusion matrix.
- [ ] ROC-AUC nếu phù hợp.
- [ ] Calibration/confidence distribution.
- [ ] Failure cases.
- [ ] Export `results/metrics.json`.

## 7.9. `inference.py` cần có gì

- [ ] Load checkpoint.
- [ ] Batch inference.
- [ ] Single prediction.
- [ ] Return JSON có schema cố định.

Ví dụ output:

```json
{
  "risk_level": "high",
  "priority": 0.87,
  "needs_human_review": true,
  "confidence": 0.82,
  "top_factors": [
    "attendance_drop",
    "late_submission_count",
    "negative_feedback"
  ],
  "model_version": "impact-triage-v0.1"
}
```

## 7.10. `export_onnx.py`

- [ ] Export model sang ONNX.
- [ ] Có dummy input.
- [ ] Có kiểm tra output PyTorch vs ONNX gần giống.
- [ ] Lưu `model.onnx`.
- [ ] Ghi log export.

## 7.11. `benchmark.py`

- [ ] Đo latency CPU.
- [ ] Đo latency GPU nếu có.
- [ ] Đo throughput batch.
- [ ] So sánh eager vs `torch.compile` nếu dùng được.
- [ ] Output `latency_benchmark.json`.

## 7.12. Optimization nên show

- [ ] `torch.compile` cho inference nếu không lỗi.
- [ ] Mixed precision trên GPU nếu phù hợp.
- [ ] ONNX export cho deployment.
- [ ] Batch inference.
- [ ] Model nhỏ nhưng đủ dùng.
- [ ] Benchmark trước/sau.

## 7.13. Model Card bắt buộc

`model_card.md` phải có:

- [ ] Model name.
- [ ] Domain.
- [ ] Intended use.
- [ ] Not intended use.
- [ ] Input schema.
- [ ] Output schema.
- [ ] Training data.
- [ ] Evaluation data.
- [ ] Metrics.
- [ ] Limitations.
- [ ] Risks.
- [ ] Human oversight.
- [ ] Version.
- [ ] Reproducibility command.

## 7.14. Slide “Why PyTorch mattered”

Nội dung slide:

```text
PyTorch was used not as a library checkbox, but as the product’s risk/priority engine.

1. Custom Impact Triage model built with torch.nn.Module
2. Trained/evaluated on domain-specific operational data
3. Integrated into FastAPI inference endpoint
4. Optimized with torch.compile / ONNX export
5. Benchmarked for latency and reliability
6. Used to trigger human approval for high-risk actions
```

## 7.15. Checklist chống bị hỏi “Sao không dùng GPT hết?”

Trả lời:

```text
LLM mạnh ở ngôn ngữ, tổng hợp và giải thích. Nhưng các quyết định như ưu tiên rủi ro,
dự đoán nguy cơ hoặc phân loại mức độ cần một model nhỏ, kiểm soát được, đo được,
chạy nhanh và có thể audit. Vì vậy chúng em dùng PyTorch làm risk/triage engine,
còn LLM làm planner và communicator.
```

---

## 8. Kiến trúc AI-native nên pitch

## 8.1. Sơ đồ tối thiểu

```text
User / Operator
    ↓
Frontend Cockpit
    ↓
Backend API
    ↓
AI Orchestrator
    ├── Input Guardrail / PII Filter
    ├── Intent Router
    ├── RAG Retriever
    ├── PyTorch Risk & Priority Engine
    ├── LLM Planner
    ├── Tool Executor
    ├── Human Approval Queue
    ├── Output Guardrail
    └── Telemetry / Evaluation Logger
    ↓
Business Action
    ↓
Metrics Dashboard
```

## 8.2. Điểm ăn tiền khi nói kiến trúc

- [ ] Không nói “tụi em dùng GPT”.
- [ ] Nói “tụi em thiết kế một workflow có AI ở đúng điểm tạo giá trị”.
- [ ] Không nói “AI quyết định”.
- [ ] Nói “AI đề xuất, con người duyệt ở hành động rủi ro”.
- [ ] Không nói “dashboard”.
- [ ] Nói “cockpit hành động”.
- [ ] Không nói “model chính xác 100%”.
- [ ] Nói “có metric, confidence, audit log, fallback”.

## 8.3. Component bắt buộc trong demo

- [ ] Input thật hoặc giả lập giống thật.
- [ ] Knowledge base/policy.
- [ ] PyTorch prediction.
- [ ] LLM explanation.
- [ ] Tool action.
- [ ] Human approval.
- [ ] Trace/audit log.
- [ ] Metric dashboard.

---

## 9. UI/UX checklist để demo nhìn “xịn”

## 9.1. Màn hình chính

- [ ] Tên sản phẩm.
- [ ] Domain selector.
- [ ] Status backend/AI/PyTorch/RAG.
- [ ] Main workflow panel.
- [ ] Chat/copilot input.
- [ ] AI response có structure.
- [ ] Evidence panel.
- [ ] Action queue.
- [ ] Approval queue.
- [ ] Metrics cards.
- [ ] Trace timeline.

## 9.2. Các card nên có

- [ ] `Risk Level`
- [ ] `Priority Score`
- [ ] `Confidence`
- [ ] `Needs Human Review`
- [ ] `Evidence Sources`
- [ ] `Recommended Action`
- [ ] `Expected Impact`
- [ ] `Pilot Metric`
- [ ] `Latency`
- [ ] `Model Version`

## 9.3. Trace timeline nên show

```text
1. Input received
2. PII scanned
3. Intent routed
4. Data retrieved
5. PyTorch risk scored
6. RAG evidence retrieved
7. LLM plan generated
8. Guardrail checked
9. Human approval required
10. Action created
11. Metrics logged
```

## 9.4. UI tuyệt đối tránh

- [ ] Không để toàn bộ màn hình là chat trống.
- [ ] Không show quá nhiều menu CRUD.
- [ ] Không show JSON thô quá lâu.
- [ ] Không để giám khảo phải đọc log dài.
- [ ] Không để chữ quá nhỏ.
- [ ] Không để demo phụ thuộc hoàn toàn vào mạng.
- [ ] Không để action nguy hiểm chạy tự động.

---

## 10. Demo 7 phút — kịch bản chuẩn

## 10.1. Cấu trúc

```text
0:00–0:45 — Problem
0:45–1:30 — Data & current workflow
1:30–2:30 — AI-native architecture
2:30–5:30 — Live demo main flow
5:30–6:15 — Metrics & pilot
6:15–7:00 — Trust, PyTorch, closing
```

## 10.2. Script mẫu dùng được cho mọi domain

### Mở đầu

```text
Vấn đề tụi em chọn không phải là tạo thêm một chatbot.
Vấn đề là trong vận hành thực tế, dữ liệu nằm rời rạc, con người bị quá tải,
và quyết định quan trọng thường bị đưa ra muộn hoặc thiếu căn cứ.
```

### Chuyển sang giải pháp

```text
Giải pháp của tụi em là một AI-native workflow copilot.
Hệ thống nhận dữ liệu thật, dùng PyTorch để đánh giá rủi ro/ưu tiên,
dùng RAG để bám chính sách, dùng LLM để lập kế hoạch,
và chỉ thực thi hành động sau khi con người duyệt.
```

### Chuyển sang demo

```text
Bây giờ em sẽ demo một luồng chính: từ dữ liệu đầu vào đến hành động được duyệt.
```

### Chốt

```text
Điểm chính không nằm ở việc AI trả lời hay.
Điểm chính là AI biến dữ liệu thành hành động có kiểm soát, đo được và có thể pilot.
```

## 10.3. Demo flow bắt buộc

- [ ] Bước 1: Chọn domain.
- [ ] Bước 2: Seed hoặc upload dữ liệu.
- [ ] Bước 3: Gửi câu hỏi/vấn đề.
- [ ] Bước 4: PyTorch model tạo risk/priority.
- [ ] Bước 5: RAG lấy chính sách/ngữ cảnh.
- [ ] Bước 6: LLM tạo giải thích/kế hoạch.
- [ ] Bước 7: Tool tạo task/ticket/report.
- [ ] Bước 8: Human approval.
- [ ] Bước 9: Metrics cập nhật.

## 10.4. Một “wow moment” nên có

Chọn 1 trong 3:

### Wow moment giáo dục

```text
AI phát hiện 5 sinh viên có nguy cơ rớt môn trước khi điểm cuối kỳ xảy ra,
giải thích nguyên nhân từng người và tạo kế hoạch can thiệp cá nhân hóa.
```

### Wow moment nông nghiệp

```text
AI không kết luận vội từ ảnh; nó kết hợp ảnh + thời tiết + nhật ký chăm sóc,
sau đó tạo lịch theo dõi 7 ngày và yêu cầu chuyên gia duyệt khi rủi ro cao.
```

### Wow moment SME

```text
AI đọc bán hàng + tồn kho + phản hồi khách, phát hiện 3 vấn đề ưu tiên hôm nay,
rồi tạo action cho chủ doanh nghiệp duyệt.
```

---

## 11. Pitch deck 8 slide

## Slide 1 — Title

- [ ] Tên sản phẩm.
- [ ] Tagline.
- [ ] Team FPT Polytechnic Đồng Nai.
- [ ] Một hình UI/sản phẩm.

## Slide 2 — Problem

- [ ] Người dùng chính.
- [ ] Tình huống đau.
- [ ] Thiệt hại đo được hoặc mô tả cụ thể.
- [ ] Current workflow thủ công/rời rạc.

## Slide 3 — Why now / Why AI-native

- [ ] Vì sao dashboard/CRUD không đủ.
- [ ] AI xử lý ngữ cảnh, dự đoán, ưu tiên, gợi ý, tổng hợp.
- [ ] Sản phẩm là workflow, không phải chatbot.

## Slide 4 — Solution

- [ ] Input.
- [ ] AI processing.
- [ ] Human approval.
- [ ] Action.
- [ ] Metric.

## Slide 5 — Architecture

- [ ] FE.
- [ ] BE.
- [ ] AI Orchestrator.
- [ ] RAG.
- [ ] PyTorch Engine.
- [ ] Tools.
- [ ] Guardrails.
- [ ] Telemetry.

## Slide 6 — Demo / Product

- [ ] 3 ảnh màn hình.
- [ ] Luồng chính 1 câu.
- [ ] Kết quả trước/sau.

## Slide 7 — Trust, Risk, Human-in-the-loop

- [ ] PII.
- [ ] Hallucination.
- [ ] Confidence.
- [ ] Approval.
- [ ] Audit log.
- [ ] Fallback.

## Slide 8 — Pilot & Impact

- [ ] Pilot 2 tuần.
- [ ] 1 lớp / 1 cửa hàng / 1 nhóm / 1 vườn.
- [ ] 100–300 mẫu.
- [ ] Metric pass/fail.
- [ ] Roadmap scale.

## Slide bonus — PyTorch Award

- [ ] Model architecture.
- [ ] Dataset.
- [ ] Metrics.
- [ ] Benchmark.
- [ ] Integration point.
- [ ] Why PyTorch mattered.

---

## 12. Product Canvas mẫu

Tạo file `domains/<domain>/product_canvas.md`.

```markdown
# Product Canvas

## 1. User
- User trực tiếp:
- Người ra quyết định:
- Người bị ảnh hưởng:

## 2. Pain
- Pain chính:
- Tình huống cụ thể:
- Thiệt hại hiện tại:
- Vì sao đang xử lý kém:

## 3. Current Workflow
- Dữ liệu đang nằm ở đâu:
- Ai xử lý:
- Mất bao lâu:
- Bỏ sót ở đâu:

## 4. AI Role
- AI phân loại:
- AI dự đoán:
- AI gợi ý:
- AI tổng hợp:
- AI tạo hành động:

## 5. Data
- Dữ liệu đầu vào:
- Nguồn dữ liệu:
- Dữ liệu mô phỏng:
- Dữ liệu cần trong pilot:

## 6. Output
- Cảnh báo:
- Ưu tiên:
- Kế hoạch:
- Task:
- Báo cáo:

## 7. Human-in-the-loop
- Hành động nào cần duyệt:
- Ai duyệt:
- Khi nào AI bị chặn:
- Log gì được lưu:

## 8. Metric
- Thời gian:
- Độ chính xác:
- Tỷ lệ bỏ sót:
- Chi phí:
- Mức hài lòng:

## 9. Risk
- Sai dự đoán:
- Lộ dữ liệu:
- Hallucination:
- Người dùng quá tin AI:
- Thiên lệch:

## 10. Pilot Scope
- Phạm vi:
- Thời gian:
- Số mẫu:
- Tiêu chí pass:
- Tiêu chí stop:
```

---

## 13. Pilot plan mẫu

Tạo file `docs/06_pilot_pathway.md` và mỗi domain có bản riêng.

```markdown
# Pilot Pathway

## Phase 1 — Discovery
- Thời gian: 1–2 ngày
- Mục tiêu: xác nhận pain, user, workflow
- Output: problem brief + workflow map

## Phase 2 — Prototype
- Thời gian: 3–5 ngày
- Mục tiêu: demo 1 luồng chính
- Output: prototype + eval cases

## Phase 3 — Shadow Mode
- Thời gian: 1 tuần
- Mục tiêu: AI chạy song song, chưa tự động quyết định
- Output: so sánh AI vs người thật

## Phase 4 — Limited Pilot
- Thời gian: 2 tuần
- Phạm vi: 1 lớp / 1 cửa hàng / 1 nhóm vận hành / 1 vườn
- Mẫu: 100–300 records
- Output: báo cáo trước/sau

## Phase 5 — Scale / Iterate / Stop
- Nếu đạt metric: mở rộng
- Nếu chưa đạt: chỉnh model/workflow
- Nếu không có giá trị: dừng
```

## Metric pass/fail mẫu

- [ ] Giảm ít nhất 30% thời gian xử lý.
- [ ] Giảm ít nhất 20% số trường hợp bỏ sót.
- [ ] Ít nhất 80% đề xuất AI được người dùng đánh giá hữu ích.
- [ ] 100% hành động rủi ro cao có human approval.
- [ ] Dưới 5% câu trả lời không có căn cứ.
- [ ] Latency trung bình dưới 3–5 giây cho prediction/action chính.

---

## 14. Evaluation checklist

## 14.1. AI evaluation

- [ ] Intent classification accuracy.
- [ ] Risk prediction F1.
- [ ] Priority ranking quality.
- [ ] RAG groundedness.
- [ ] Hallucination rate.
- [ ] Human approval trigger accuracy.
- [ ] False positive/false negative analysis.
- [ ] Latency.

## 14.2. Product evaluation

- [ ] Thời gian xử lý trước/sau.
- [ ] Số bước thủ công giảm.
- [ ] Tỷ lệ task tạo đúng.
- [ ] Tỷ lệ đề xuất được duyệt.
- [ ] Tỷ lệ người dùng phải sửa lại output.
- [ ] Mức hài lòng giả lập/pilot.
- [ ] Tính dễ hiểu của UI.

## 14.3. Demo reliability

- [ ] Chạy demo 10 lần liên tục.
- [ ] Ghi lại số lần lỗi.
- [ ] Ghi latency trung bình.
- [ ] Ghi lỗi API/model/network.
- [ ] Có fallback cho từng lỗi.

## 14.4. File `docs/08_evaluation_report.md`

```markdown
# Evaluation Report

## Dataset
- Domain:
- Number of samples:
- Train/val/test split:
- Synthetic data generation method:

## PyTorch Model Metrics
| Metric | Value |
|---|---|
| Accuracy | |
| F1 | |
| Recall high-risk | |
| Latency CPU | |
| Latency GPU | |

## RAG Metrics
| Metric | Value |
|---|---|
| Grounded answer rate | |
| Missing evidence rate | |
| Citation correctness | |

## Workflow Metrics
| Metric | Before | After | Improvement |
|---|---:|---:|---:|
| Avg handling time | | | |
| Missed cases | | | |
| Human review coverage | | | |

## Failure Cases
- Case 1:
- Case 2:
- Case 3:

## Limitations
- 
```

---

## 15. Guardrails & Trust checklist

## 15.1. Input guardrails

- [ ] Detect PII: tên, số điện thoại, email, mã sinh viên, địa chỉ.
- [ ] Mask PII trong logs.
- [ ] Chặn prompt injection cơ bản.
- [ ] Validate file upload.
- [ ] Validate domain schema.
- [ ] Chặn input ngoài phạm vi domain.

## 15.2. Model guardrails

- [ ] Confidence threshold.
- [ ] Low-confidence → hỏi thêm dữ kiện.
- [ ] High-risk → human approval.
- [ ] Không claim chắc chắn trong y tế/nông nghiệp/rủi ro cao.
- [ ] Log model version.
- [ ] Log prediction factors.

## 15.3. Output guardrails

- [ ] Không đưa lời khuyên nguy hiểm.
- [ ] Không tự động gửi tin nhắn nhạy cảm.
- [ ] Không tự động hoàn tiền/hủy/đánh giá/kỷ luật.
- [ ] Có disclaimer đúng mức.
- [ ] Có evidence/source.
- [ ] Có nút “duyệt/sửa/từ chối”.

## 15.4. Audit log

- [ ] User input.
- [ ] Retrieved evidence.
- [ ] PyTorch prediction.
- [ ] LLM plan.
- [ ] Tool action.
- [ ] Approval decision.
- [ ] Timestamp.
- [ ] User/admin.
- [ ] Final status.

---

## 16. Backend/API checklist

## 16.1. API tối thiểu

- [ ] `GET /health`
- [ ] `GET /api/status`
- [ ] `POST /api/domain/switch`
- [ ] `POST /api/seed`
- [ ] `POST /api/chat`
- [ ] `POST /api/analyze`
- [ ] `POST /api/pytorch/predict`
- [ ] `GET /api/approvals`
- [ ] `POST /api/approvals/{id}/approve`
- [ ] `POST /api/approvals/{id}/reject`
- [ ] `GET /api/metrics`
- [ ] `GET /api/trace/{id}`
- [ ] `POST /api/eval/run`

## 16.2. Response schema chuẩn

```json
{
  "answer": "...",
  "intent": "...",
  "risk": {
    "level": "high",
    "confidence": 0.82,
    "needs_human_review": true
  },
  "evidence": [
    {
      "source": "policy.md",
      "chunk": "...",
      "score": 0.78
    }
  ],
  "actions": [
    {
      "type": "create_task",
      "status": "pending_approval"
    }
  ],
  "trace": [
    {
      "step": "pytorch_risk_engine",
      "duration_ms": 18,
      "status": "ok"
    }
  ],
  "metrics": {
    "estimated_time_saved_minutes": 12
  }
}
```

## 16.3. Error handling

- [ ] Nếu LLM lỗi → trả fallback rule-based/demo response.
- [ ] Nếu PyTorch lỗi → dùng heuristic fallback nhưng báo rõ.
- [ ] Nếu RAG lỗi → trả “không đủ căn cứ”.
- [ ] Nếu tool lỗi → tạo pending action thủ công.
- [ ] Nếu frontend mất kết nối → có video backup.
- [ ] Không để stack trace hiện ra trên màn hình demo.

---

## 17. Frontend checklist

## 17.1. Màn hình cần có

- [ ] Landing/Product overview.
- [ ] AI Copilot cockpit.
- [ ] Domain selector.
- [ ] Data preview.
- [ ] Main chat/action input.
- [ ] PyTorch prediction card.
- [ ] Evidence/RAG card.
- [ ] Human approval queue.
- [ ] Action/task board.
- [ ] Metrics dashboard.
- [ ] Trace timeline.
- [ ] Demo mode toggle.

## 17.2. Demo mode

- [ ] Có nút load sample scenario.
- [ ] Có nút reset data.
- [ ] Có nút run main demo.
- [ ] Có nút copy sample prompt.
- [ ] Có trạng thái “offline fallback”.
- [ ] Có precomputed response nếu API lỗi.
- [ ] Có keyboard shortcut hoặc button rõ cho presenter.

## 17.3. Visual language

- [ ] Trông như sản phẩm doanh nghiệp, không như bài tập sinh viên.
- [ ] Font rõ.
- [ ] Card ít chữ.
- [ ] Số liệu lớn.
- [ ] Nút hành động nổi bật.
- [ ] Trace gọn.
- [ ] Không dùng quá nhiều màu.
- [ ] Không để UI rối vì muốn show nhiều.

---

## 18. Data checklist

## 18.1. Dữ liệu mẫu phải giống thật

- [ ] Có 100–300 records.
- [ ] Có trường hợp bình thường.
- [ ] Có trường hợp rủi ro thấp.
- [ ] Có trường hợp rủi ro trung bình.
- [ ] Có trường hợp rủi ro cao.
- [ ] Có missing values.
- [ ] Có noise nhẹ.
- [ ] Có dữ liệu phi cấu trúc: message, note, feedback.
- [ ] Có policy/knowledge base.
- [ ] Có expected output để eval.

## 18.2. Không nên

- [ ] Không dùng dữ liệu quá sạch như demo giả.
- [ ] Không dùng tên công ty thật nếu không có quyền.
- [ ] Không dùng dữ liệu cá nhân thật.
- [ ] Không tạo data vô lý.
- [ ] Không để data toàn tiếng Anh nếu pitch tiếng Việt.
- [ ] Không để schema không giải thích được.

## 18.3. Synthetic data README

Mỗi domain cần có:

```markdown
# Synthetic Data README

## Purpose
Dữ liệu mô phỏng phục vụ prototype 48h.

## Schema
Mô tả từng file và từng cột.

## Generation Method
Dữ liệu được tạo giả lập dựa trên workflow thực tế, không chứa dữ liệu cá nhân thật.

## Known Limitations
Không đại diện hoàn toàn cho dữ liệu doanh nghiệp thật.

## Pilot Data Needed
Khi pilot cần dữ liệu thật từ...
```

---

## 19. Lịch chuẩn bị từ hôm nay đến ngày thi

## T-14 đến T-10

- [ ] Dọn repo.
- [ ] Tách domain pack.
- [ ] Viết lại README.
- [ ] Tạo PyTorch engine skeleton.
- [ ] Tạo model train/eval nhanh.
- [ ] Tạo synthetic data generator.
- [ ] Tạo docs template.
- [ ] Tạo pitch deck template.
- [ ] Chạy thử Docker/ngrok.
- [ ] Quay video demo kỹ thuật hiện tại.

## T-9 đến T-7

- [ ] Hoàn thiện domain education.
- [ ] Hoàn thiện domain SME.
- [ ] Hoàn thiện domain agriculture.
- [ ] Test switch domain.
- [ ] Test PyTorch model với 3 domain.
- [ ] Tạo model card.
- [ ] Tạo benchmark.
- [ ] Tạo evaluation report mẫu.
- [ ] Tạo Q&A giám khảo.

## T-6 đến T-4

- [ ] UI polish.
- [ ] Thêm demo mode.
- [ ] Thêm approval queue đẹp.
- [ ] Thêm trace timeline.
- [ ] Thêm metrics dashboard.
- [ ] Viết pitch 3 phút.
- [ ] Viết demo 7 phút.
- [ ] Rehearsal lần 1.
- [ ] Sửa lỗi theo rehearsal.

## T-3 đến T-2

- [ ] Freeze core code.
- [ ] Chỉ sửa bug, không thêm feature lớn.
- [ ] Quay video demo backup.
- [ ] Xuất slide PDF.
- [ ] In/backup cheat sheet.
- [ ] Test trên máy thi/laptop.
- [ ] Test mạng 4G/5G.
- [ ] Test offline mode.
- [ ] Tạo bản zip repo.

## T-1

- [ ] Chạy full demo 10 lần.
- [ ] Chạy bằng tài khoản/máy sẽ đem đi thi.
- [ ] Pin dependency.
- [ ] Backup `.env`.
- [ ] Backup Docker image nếu được.
- [ ] Backup video.
- [ ] Backup slide.
- [ ] Backup dữ liệu.
- [ ] Backup checkpoint model.
- [ ] Sạc toàn bộ thiết bị.
- [ ] Ngủ đủ.

---

## 20. Chiến thuật 48 giờ trong cuộc thi

## Giờ 0–1: Đọc đề

- [ ] Không code.
- [ ] Đọc toàn bộ đề.
- [ ] Xác định user.
- [ ] Xác định pain.
- [ ] Xác định data.
- [ ] Chọn domain gần nhất.
- [ ] Chấm bằng bảng 10 tiêu chí.
- [ ] Chốt bài.

## Giờ 1–3: Product canvas

- [ ] Viết problem brief 1 trang.
- [ ] Vẽ current workflow.
- [ ] Vẽ AI-native workflow.
- [ ] Chốt PyTorch task.
- [ ] Chốt demo flow.
- [ ] Chốt metric.
- [ ] Chốt risk/HITL.
- [ ] Chốt phân công.

## Giờ 3–6: Setup repo/domain

- [ ] Switch domain.
- [ ] Sửa data schema.
- [ ] Seed data.
- [ ] Sửa prompt.
- [ ] Sửa knowledge base.
- [ ] Sửa tool action.
- [ ] Chạy smoke test.

## Giờ 6–12: Core demo

- [ ] Backend chạy ổn.
- [ ] Frontend hiển thị đúng domain.
- [ ] PyTorch model inference được.
- [ ] RAG lấy evidence được.
- [ ] LLM planner trả JSON đúng.
- [ ] Tool action tạo được task/report.
- [ ] Approval queue hoạt động.

## Giờ 12–20: PyTorch + evaluation

- [ ] Train hoặc fine-tune nhanh.
- [ ] Evaluate.
- [ ] Benchmark.
- [ ] Export model.
- [ ] Model card.
- [ ] UI hiển thị PyTorch output.
- [ ] Chuẩn bị slide PyTorch.

## Giờ 20–28: Product polish

- [ ] UI đẹp.
- [ ] Copywriting rõ.
- [ ] Demo mode.
- [ ] Trace timeline.
- [ ] Metrics.
- [ ] Error handling.
- [ ] Fallback responses.

## Giờ 28–36: Pitch + docs

- [ ] Slide 8 trang.
- [ ] Demo script.
- [ ] Judge Q&A.
- [ ] Pilot plan.
- [ ] Risk plan.
- [ ] README final.
- [ ] Technical report.

## Giờ 36–42: Rehearsal

- [ ] Chạy demo 5 lần.
- [ ] Bấm giờ.
- [ ] Người pitch tập.
- [ ] Người demo tập.
- [ ] Người backup chuẩn bị.
- [ ] Cắt bớt nếu quá dài.
- [ ] Sửa câu chữ.

## Giờ 42–46: Freeze

- [ ] Không thêm feature.
- [ ] Chỉ sửa lỗi.
- [ ] Quay video backup.
- [ ] Export slide PDF.
- [ ] Tạo release tag.
- [ ] Backup repo zip.
- [ ] Backup database.

## Giờ 46–48: Trình diễn

- [ ] Mở sẵn tab demo.
- [ ] Mở sẵn slide.
- [ ] Mở sẵn terminal health check.
- [ ] Tắt app không cần thiết.
- [ ] Test máy chiếu.
- [ ] Test âm thanh.
- [ ] Người pitch bình tĩnh.
- [ ] Không xin lỗi lan man nếu lỗi, chuyển fallback ngay.

---

## 21. Phân công team

## 21.1. Team Lead / Product — Khải

- [ ] Chốt bài toán.
- [ ] Chốt scope.
- [ ] Chốt metric.
- [ ] Chốt pilot.
- [ ] Chống lan man.
- [ ] Quyết định bỏ feature.
- [ ] Duyệt pitch.
- [ ] Trả lời câu hỏi khó.
- [ ] Giữ nhịp 48h.

Deliverable:

- [ ] Problem brief.
- [ ] Product canvas.
- [ ] Pilot plan.
- [ ] Q&A.
- [ ] Final pitch.

## 21.2. AI / PyTorch

- [ ] Chọn PyTorch task.
- [ ] Build dataset.
- [ ] Train model.
- [ ] Evaluate.
- [ ] Benchmark.
- [ ] Export.
- [ ] Model card.
- [ ] API inference.
- [ ] Slide PyTorch.

Deliverable:

- [ ] `ai_layer/pytorch_engine/`
- [ ] `results/metrics.json`
- [ ] `model_card.md`
- [ ] `benchmark.json`

## 21.3. RAG / Prompt / Orchestrator

- [ ] Domain knowledge base.
- [ ] Chunking.
- [ ] Retrieval.
- [ ] Prompt.
- [ ] JSON schema.
- [ ] Guardrails.
- [ ] Tool plan.
- [ ] Trace.

Deliverable:

- [ ] RAG pipeline.
- [ ] Prompt templates.
- [ ] Eval cases.
- [ ] Guardrail rules.

## 21.4. Fullstack

- [ ] API.
- [ ] Frontend.
- [ ] Dashboard.
- [ ] Action queue.
- [ ] Approval queue.
- [ ] Metrics.
- [ ] Deployment.
- [ ] Error handling.

Deliverable:

- [ ] Product demo chạy ổn.
- [ ] UI đẹp.
- [ ] Health check.
- [ ] Demo mode.

## 21.5. Business / Pitch / Design

- [ ] Slide.
- [ ] Story.
- [ ] Visual.
- [ ] Demo script.
- [ ] Video backup.
- [ ] Judge Q&A.
- [ ] Timing.

Deliverable:

- [ ] Pitch deck.
- [ ] Demo video.
- [ ] One-page handout.
- [ ] Closing line.

## 21.6. QA / Ops

- [ ] Test demo.
- [ ] Test fallback.
- [ ] Test install.
- [ ] Test data.
- [ ] Test network.
- [ ] Test video.
- [ ] Ghi bug.
- [ ] Confirm freeze.

Deliverable:

- [ ] Test report.
- [ ] Bug list.
- [ ] Backup checklist.
- [ ] Day-D runbook.

---

## 22. Judge Q&A — câu khó và đáp án

## 22.1. “Khác gì chatbot?”

```text
Chatbot chủ yếu trả lời hội thoại. Sản phẩm của chúng em là workflow copilot:
có dữ liệu nghiệp vụ, RAG, PyTorch risk engine, tool action, human approval,
trace log và metric. AI không chỉ nói, mà biến dữ liệu thành hành động có kiểm soát.
```

## 22.2. “Sao không dùng dashboard thường?”

```text
Dashboard mô tả điều đã xảy ra. Hệ thống của chúng em đọc ngữ cảnh,
dự đoán/ưu tiên rủi ro, gợi ý hành động tiếp theo và tạo task cho người dùng duyệt.
Nó hỗ trợ ra quyết định, không chỉ hiển thị số liệu.
```

## 22.3. “AI sai thì sao?”

```text
Các hành động rủi ro cao không được tự động thực thi. Hệ thống có confidence,
guardrail, evidence, trace log và human-in-the-loop. AI đề xuất, con người duyệt.
```

## 22.4. “Dữ liệu thật lấy ở đâu?”

```text
Giai đoạn đầu không cần tích hợp toàn bộ hệ thống. Pilot có thể bắt đầu từ Excel,
form, email, log hiện có hoặc export từ hệ thống đang dùng. Sau đó mới tích hợp sâu.
```

## 22.5. “Sao cần PyTorch, dùng LLM hết không được à?”

```text
LLM mạnh ở tổng hợp và giải thích, nhưng các tín hiệu như risk, priority,
severity cần một model nhỏ, đo được, chạy nhanh, có thể audit. PyTorch model
đóng vai trò risk/priority engine; LLM chỉ lập kế hoạch và diễn giải.
```

## 22.6. “Model train bằng data giả có đáng tin không?”

```text
Trong hackathon 48h, dữ liệu mô phỏng dùng để chứng minh prototype và workflow.
Pilot pathway của chúng em có phase shadow mode để so sánh AI với người thật
trên dữ liệu thực trước khi vận hành.
```

## 22.7. “Có scale được không?”

```text
Có, vì kiến trúc tách domain data, RAG, PyTorch engine, tool action và UI.
Khi đổi domain, thay knowledge base, schema, tool và eval cases, không phải viết lại toàn bộ.
```

## 22.8. “Có thay con người không?”

```text
Không. Sản phẩm giúp con người ra quyết định nhanh hơn, có căn cứ hơn và ít bỏ sót hơn.
Các quyết định quan trọng vẫn có người duyệt.
```

## 22.9. “Nếu doanh nghiệp lớn như KFC/Jollibee thì sao?”

```text
MVP không claim thay ERP hay vận hành toàn tập đoàn. Giai đoạn đầu pilot ở một cửa hàng,
một nhóm dữ liệu hoặc một quy trình cụ thể. Khi có metric tốt mới mở rộng.
```

## 22.10. “Tính mới nằm ở đâu?”

```text
Tính mới không nằm ở việc có chatbot hay agent, mà ở cách đóng gói thành workflow AI-native:
PyTorch risk engine + RAG evidence + LLM planner + tool action + human approval + telemetry + pilot metrics.
```

---

## 23. Bộ file phải có trước khi nộp

## 23.1. Tài liệu sản phẩm

- [ ] `problem_brief.md`
- [ ] `product_canvas.md`
- [ ] `pilot_plan.md`
- [ ] `risk_and_guardrails.md`
- [ ] `evaluation_report.md`
- [ ] `business_model.md`
- [ ] `architecture.md`
- [ ] `demo_script.md`
- [ ] `judge_qa.md`

## 23.2. Tài liệu kỹ thuật

- [ ] `README.md`
- [ ] `technical_report.md`
- [ ] `api_docs.md`
- [ ] `pytorch_model_card.md`
- [ ] `pytorch_benchmark.md`
- [ ] `deployment_guide.md`
- [ ] `.env.example`
- [ ] `docker-compose.yml`

## 23.3. Demo assets

- [ ] Slide PPTX/PDF.
- [ ] Video backup.
- [ ] Screenshot.
- [ ] Sample inputs.
- [ ] Sample outputs.
- [ ] Fallback script.
- [ ] One-page handout.
- [ ] Architecture diagram PNG.
- [ ] QR code repo/demo nếu cần.

## 23.4. Code assets

- [ ] Frontend.
- [ ] Backend.
- [ ] AI orchestrator.
- [ ] RAG.
- [ ] Tools.
- [ ] Guardrails.
- [ ] PyTorch model.
- [ ] Evaluation.
- [ ] Tests.
- [ ] Seed data.
- [ ] Scripts.

---

## 24. Hardware / môi trường thi checklist

## 24.1. Laptop/máy

- [ ] Laptop chính chạy được demo.
- [ ] Laptop phụ có repo.
- [ ] Sạc laptop.
- [ ] Ổ cắm.
- [ ] Dây HDMI/USB-C.
- [ ] Chuột.
- [ ] Bàn phím nếu cần.
- [ ] Điện thoại phát 4G/5G.
- [ ] Pin dự phòng.
- [ ] Tai nghe/mic nếu cần.
- [ ] USB chứa backup.

## 24.2. Software

- [ ] Node version cố định.
- [ ] Python version cố định.
- [ ] Docker chạy được.
- [ ] Ollama/LLM local nếu dùng.
- [ ] Model checkpoint local.
- [ ] Dataset local.
- [ ] `.env` local.
- [ ] Browser đã login.
- [ ] Git branch sạch.
- [ ] Không phụ thuộc package chưa cài.
- [ ] Không phụ thuộc internet để chạy demo chính.

## 24.3. Backup

- [ ] Repo zip.
- [ ] Docker image export nếu có.
- [ ] Video demo.
- [ ] Slide PDF.
- [ ] Slide PPTX.
- [ ] Dữ liệu mẫu.
- [ ] Checkpoint.
- [ ] `.env` riêng, không public.
- [ ] Screenshot.
- [ ] Script thuyết trình in ra.

---

## 25. Checklist chất lượng trước giờ trình bày

## 25.1. Demo test

- [ ] Backend health OK.
- [ ] Frontend mở OK.
- [ ] PyTorch endpoint OK.
- [ ] RAG endpoint OK.
- [ ] Chat endpoint OK.
- [ ] Approval OK.
- [ ] Metrics OK.
- [ ] Reset demo OK.
- [ ] Video backup OK.

## 25.2. Pitch test

- [ ] Pitch dưới thời gian quy định.
- [ ] Không nói quá nhanh.
- [ ] Không dùng quá nhiều thuật ngữ.
- [ ] Pain rõ trong 30 giây.
- [ ] Demo không quá 7 phút.
- [ ] Có câu chốt mạnh.
- [ ] Có người backup trả lời kỹ thuật.
- [ ] Có người backup bật video nếu lỗi.

## 25.3. Slide test

- [ ] Không quá nhiều chữ.
- [ ] Font đủ lớn.
- [ ] Có architecture rõ.
- [ ] Có metric.
- [ ] Có PyTorch slide.
- [ ] Có pilot slide.
- [ ] Có risk/HITL slide.
- [ ] Có screenshot sản phẩm.

---

## 26. Công thức trình bày cuối

## 26.1. Opening line

```text
Chúng em không xây dựng một chatbot.
Chúng em xây dựng một AI-native workflow copilot giúp biến dữ liệu rời rạc
thành hành động có kiểm soát, đo được và có thể pilot trong môi trường thật.
```

## 26.2. PyTorch line

```text
PyTorch là phần tạo tín hiệu rủi ro và ưu tiên trong sản phẩm.
LLM giúp giải thích và lập kế hoạch, nhưng quyết định rủi ro được đo bằng model riêng,
có evaluate, benchmark và human approval.
```

## 26.3. Pilot line

```text
Sau cuộc thi, sản phẩm có thể pilot theo shadow mode trong 2 tuần với 100–300 mẫu,
đo thời gian xử lý, tỷ lệ bỏ sót, độ tin cậy của AI và mức độ chấp nhận của người dùng.
```

## 26.4. Closing line

```text
Điểm chúng em muốn chứng minh là: AI tốt không phải AI thay con người,
mà là AI giúp con người ra quyết định nhanh hơn, đúng hơn và có kiểm soát hơn.
```

---

## 27. Bộ “không được làm”

- [ ] Không đổi đề quá muộn sau 6 giờ đầu.
- [ ] Không thêm feature lớn sau giờ 36.
- [ ] Không pitch quá rộng.
- [ ] Không hứa triển khai toàn quốc/toàn ngành nếu chưa có căn cứ.
- [ ] Không nói AI chính xác tuyệt đối.
- [ ] Không giấu việc dữ liệu là synthetic.
- [ ] Không để PyTorch chỉ là phụ kiện.
- [ ] Không để demo chỉ là chat.
- [ ] Không show CRUD quá nhiều.
- [ ] Không để giám khảo hỏi “vậy AI nằm ở đâu?”.
- [ ] Không để giám khảo hỏi “vậy PyTorch nằm ở đâu?”.
- [ ] Không để giám khảo hỏi “pilot kiểu gì?” mà không trả lời được.
- [ ] Không để hệ thống tự động làm hành động rủi ro cao.
- [ ] Không cãi lan man với giám khảo.
- [ ] Không xin lỗi dài nếu demo lỗi; chuyển fallback ngay.

---

## 28. Bộ “phải làm”

- [ ] Một pain thật.
- [ ] Một user chính.
- [ ] Một workflow chính.
- [ ] Một AI-native architecture.
- [ ] Một PyTorch model thật.
- [ ] Một demo mượt.
- [ ] Một metric rõ.
- [ ] Một pilot pathway.
- [ ] Một human approval mechanism.
- [ ] Một evaluation report.
- [ ] Một model card.
- [ ] Một video backup.
- [ ] Một pitch sắc.
- [ ] Một Q&A chắc.

---

## 29. Self-score trước khi nộp

Chấm mỗi mục 1–5.

| Nhóm | Điểm |
|---|---:|
| Pain rõ | |
| AI-fit | |
| Data hợp lý | |
| Demo mượt | |
| PyTorch thật | |
| Evaluation | |
| UI/UX | |
| Guardrails | |
| Pilot pathway | |
| Pitch/storytelling | |
| Technical reliability | |
| Business impact | |

- [ ] Tổng dưới 45/60: chưa nên tự tin.
- [ ] Tổng 45–52/60: có cửa vào nhóm mạnh.
- [ ] Tổng 53+/60: có cửa tranh giải cao.
- [ ] PyTorch dưới 4/5: khó ăn Best PyTorch Award.
- [ ] Demo dưới 4/5: rất nguy hiểm dù code tốt.

---

## 30. Final one-page checklist

## Trước ngày thi

- [ ] Repo sạch.
- [ ] README mạnh.
- [ ] 3 domain pack.
- [ ] PyTorch engine.
- [ ] Model card.
- [ ] Evaluation report.
- [ ] Demo mode.
- [ ] Pitch deck template.
- [ ] Q&A.
- [ ] Video backup.
- [ ] Docker/local run OK.

## Trong 6 giờ đầu

- [ ] Chọn bài bằng scoring matrix.
- [ ] Chốt user.
- [ ] Chốt pain.
- [ ] Chốt data.
- [ ] Chốt PyTorch task.
- [ ] Chốt demo flow.
- [ ] Chốt metric.
- [ ] Chốt pilot.

## Trước lúc trình bày

- [ ] Demo chạy 10 lần.
- [ ] Video backup mở được.
- [ ] Slide PDF mở được.
- [ ] PyTorch output hiển thị rõ.
- [ ] Human approval hiển thị rõ.
- [ ] Metric hiển thị rõ.
- [ ] Người pitch thuộc opening/closing.
- [ ] Người kỹ thuật thuộc Q&A.
- [ ] Người backup biết chuyển video.

---

# Chốt chiến thuật

Để lụm Giải Nhất, team cần chứng minh: **đúng bài toán, đúng người dùng, đúng workflow, đúng tác động**.

Để lụm Best PyTorch Award, team cần chứng minh: **PyTorch là phần lõi tạo tín hiệu kỹ thuật có đo lường, có tối ưu, có tích hợp vào sản phẩm**, không phải một notebook phụ.

Câu cuối để cả team nhớ:

```text
Một bài toán thật.
Một luồng demo sắc.
Một PyTorch engine thật.
Một cơ chế human approval rõ.
Một metric đo được.
Một pilot pathway đáng tin.
```
