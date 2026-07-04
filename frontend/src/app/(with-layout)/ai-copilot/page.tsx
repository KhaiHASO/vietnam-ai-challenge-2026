"use client";

import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, CardBody, CardHeader, Button, Table, Badge, Input, Alert } from "reactstrap";
import FeatherIcon from "feather-icons-react";

interface ServiceInfo {
  status: string;
  log: string;
}

interface Booking {
  booking_id: string;
  sport: string;
  court: string;
  date: string;
  time: string;
  amount: number;
  status: string;
}

interface Ticket {
  ticket_id: string;
  title: string;
  service: string;
  description: string;
  priority: string;
  status: string;
}

interface Student {
  student_id: string;
  name: string;
  major: string;
  prior_gpa: number;
  attendance_rate: number;
  late_submissions_count: number;
  lms_activity_score: number;
  midterm_grade: number;
}

interface InterventionLog {
  log_id: string;
  student_id: string;
  intervention_type: string;
  note: string;
  status: string;
}

interface Farm {
  farm_id: string;
  name: string;
  crop_type: string;
  leaf_damage_percent: number;
  temperature: number;
  humidity: number;
  soil_moisture: number;
  days_since_last_treatment: number;
}

interface TreatmentLog {
  log_id: string;
  crop_id: string;
  treatment_type: string;
  notes: string;
  status: string;
}

interface Approval {
  approval_id: string;
  action_type: string;
  details: Record<string, any>;
  status: string;
}

interface DbState {
  wallet?: { balance: number; currency: string };
  services: Record<string, ServiceInfo>;
  bookings?: Booking[];
  tickets?: Ticket[];
  students?: Student[];
  intervention_logs?: InterventionLog[];
  farms?: Farm[];
  treatment_logs?: TreatmentLog[];
  pending_approvals?: Approval[];
}

export default function AICopilotDashboard() {
  const [query, setQuery] = useState("");
  const [activeDomain, setActiveDomain] = useState("sme");
  const [modelName, setModelName] = useState("llama3.2");
  
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    { role: "assistant", content: "Xin chào! Tôi là Trợ lý vận hành AI-native. Hãy chọn lĩnh vực hoạt động của bạn ở trên và bắt đầu tương tác!" }
  ]);
  const [telemetry, setTelemetry] = useState<Record<string, any> | null>(null);
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [dbState, setDbState] = useState<DbState | null>(null);
  const [backendStatus, setBackendStatus] = useState<"connecting" | "online" | "offline">("connecting");
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = "http://localhost:8000";

  // Fetch db state
  const fetchDbState = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/database`);
      if (res.ok) {
        const data = await res.json();
        setDbState(data);
        setBackendStatus("online");
      } else {
        setBackendStatus("offline");
      }
    } catch (err) {
      setBackendStatus("offline");
    }
  };

  // Fetch active domain configuration
  const fetchDomainStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/domain/status`);
      if (res.ok) {
        const data = await res.json();
        setActiveDomain(data.active_domain);
        setModelName(data.model_name);
      }
    } catch (err) {
      console.error("Error fetching domain status:", err);
    }
  };

  useEffect(() => {
    fetchDomainStatus();
    fetchDbState();
    const interval = setInterval(fetchDbState, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userQuery = query;
    setMessages(prev => [...prev, { role: "user", content: userQuery }]);
    setQuery("");
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
        if (data.telemetry) {
          setTelemetry(data.telemetry);
          setSelectedStep("step_1_pii");
        }
        fetchDbState();
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "Lỗi kết nối bộ xử lý AI. Vui lòng kiểm tra backend FastAPI." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Lỗi kết nối máy chủ backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchDomain = async (domain: string) => {
    try {
      setLoading(true);
      const res = await fetch(`${BACKEND_URL}/api/domain/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain }),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveDomain(data.active_domain);
        setMessages([
          { role: "assistant", content: `Đã chuyển sang lĩnh vực: ${domain.toUpperCase()}. Tri thức RAG và dữ liệu vận hành đã được đồng bộ.` }
        ]);
        setTelemetry(null);
        setSelectedStep(null);
        fetchDbState();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/approvals/${approvalId}/approve`, { method: "POST" });
      if (res.ok) {
        fetchDbState();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/approvals/${approvalId}/reject`, { method: "POST" });
      if (res.ok) {
        fetchDbState();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetDb = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/database/reset`, { method: "POST" });
      fetchDbState();
      setMessages([{ role: "assistant", content: "Cơ sở dữ liệu của lĩnh vực đã được đặt lại về mặc định." }]);
      setTelemetry(null);
      setSelectedStep(null);
    } catch (err) {
      console.error(err);
    }
  };

  // Steps definition for trace flow visualization
  const stepsList = [
    { key: "step_1_pii", label: "1. PII Scan", desc: "Mã hóa thông tin nhạy cảm định danh." },
    { key: "step_2_input_safety", label: "2. Safety Guardrail", desc: "Lọc prompt injection & SQL injection." },
    { key: "step_3_router", label: "3. Model Router", desc: "Định tuyến Cache/FAQ/Agent." },
    { key: "step_4_rag", label: "4. CUDA RAG", desc: "Truy xuất chính sách từ Vector DB." },
    { key: "pytorch_engine", label: "5. PyTorch Triage", desc: "Dự đoán rủi ro, ưu tiên & review." },
    { key: "step_5_planner", label: "6. Agent Planner", desc: "Agent ReAct (Thought/Action)." },
    { key: "step_6_executor", label: "7. Tool Executor", desc: "Gọi các API công cụ nghiệp vụ." },
    { key: "step_7_hitl", label: "8. Human Approval", desc: "Chặn & yêu cầu quản trị viên duyệt." },
    { key: "step_8_output_safety", label: "9. Output Guardrail", desc: "Kiểm tra ảo tưởng (Hallucination)." }
  ];

  const getStepStatus = (key: string) => {
    if (!telemetry || !telemetry[key]) return "inactive";
    const data = telemetry[key];
    if (data.is_blocked || data.status === "Blocked") return "blocked";
    if (
      data.triggered || 
      data.docs_found > 0 || 
      data.steps?.length > 0 || 
      data.route || 
      data.success || 
      data.total_duration_ms || 
      data.redacted_query || 
      data.results
    ) return "active";
    return "inactive";
  };

  const blueprints: Record<string, string> = {
    step_1_pii: `def scan_and_redact(text):\n  # Mask Phone numbers & Emails\n  text = re.sub(r'0\\d{9}', '[REDACTED_PHONE]', text)\n  return text`,
    step_2_input_safety: `def check_injection(text):\n  if "bỏ qua các lệnh trước" in text.lower():\n    return Blocked(score=1.0)\n  return Safe()`,
    step_3_router: `def route(query):\n  if query in faq_cache:\n    return Route.CACHE\n  if is_action_query:\n    return Route.AGENT_MODEL`,
    step_4_rag: `def cosine_similarity(q, d):\n  return np.dot(q, d) / (norm(q) * norm(d))\n# Running SentenceTransformers locally`,
    pytorch_engine: `class ImpactTriageNet(nn.Module):\n  # Multi-task head predicting risk_level, priority_score, needs_human_review, confidence\n   risk_logits, priority_preds, review_logits, confidence = model(x)`,
    step_5_planner: `Prompt: Use ReAct pattern.\\nFormat: Thought -> Action -> Observation -> Final Answer`,
    step_6_executor: `@tool_registry.register()\\ndef create_support_ticket(title, service):\\n  # DB CRUD Write`,
    step_7_hitl: `if is_high_risk or pytorch_needs_review:\\n  create_pending_approval(action, details)`,
    step_8_output_safety: `def check_hallucination(resp, docs):\\n  # Compute overlap score between response and retrieved docs`,
  };

  return (
    <div className="page-content" style={{ padding: "80px 20px 20px 20px" }}>
      <Container fluid>
        {backendStatus === "offline" && (
          <Alert color="danger" className="d-flex align-items-center">
            <FeatherIcon icon="alert-triangle" className="me-2" />
            <div>
              <strong>FastAPI Backend offline!</strong> Vui lòng khởi chạy backend để trải nghiệm đầy đủ chức năng.
            </div>
          </Alert>
        )}

        {/* Top Header Card */}
        <Row className="mb-4">
          <Col lg={12}>
            <Card className="card overflow-hidden" style={{ borderRadius: "12px" }}>
              <CardBody className="p-4">
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
                  <div>
                    <h4 className="mb-1">
                      <Badge color="success" className="me-2 align-middle">Live</Badge>
                      Vietnam AI Challenge - Operations Copilot Cockpit
                    </h4>
                    <p className="text-muted mb-0">Hệ thống giám sát vận hành AI-Native tích hợp Guardrails & HITL</p>
                  </div>
                  
                  {/* Dynamic Domain Switcher */}
                  <div className="d-flex align-items-center gap-2 bg-light p-1 rounded">
                    <span className="fs-12 text-muted me-2 ps-2">WORKSPACE DOMAIN:</span>
                    <Button color={activeDomain === "sme" ? "primary" : "outline-secondary"} size="sm" onClick={() => handleSwitchDomain("sme")}>SME</Button>
                    <Button color={activeDomain === "education" ? "primary" : "outline-secondary"} size="sm" onClick={() => handleSwitchDomain("education")}>Education</Button>
                    <Button color={activeDomain === "agriculture" ? "primary" : "outline-secondary"} size="sm" onClick={() => handleSwitchDomain("agriculture")}>Agriculture</Button>
                  </div>

                  <div className="d-flex align-items-center gap-4 text-muted flex-wrap">
                    <div className="d-flex align-items-center gap-2">
                      <FeatherIcon icon="cpu" className="text-success" />
                      <div>
                        <div className="fs-12 text-muted">ACTIVE MODEL</div>
                        <div className="fw-bold fs-14">{modelName}</div>
                      </div>
                    </div>
                    <div className="d-flex align-items-center gap-2">
                      <FeatherIcon icon="activity" className="text-info" />
                      <div>
                        <div className="fs-12 text-muted">LATENCY</div>
                        <div className="fw-bold fs-14">
                          {telemetry?.step_9_dispatcher?.total_duration_ms ? `${telemetry.step_9_dispatcher.total_duration_ms.toFixed(1)} ms` : "0 ms"}
                        </div>
                      </div>
                    </div>
                    <div>
                      <Button color="outline-danger" size="sm" onClick={handleResetDb}>
                        <FeatherIcon icon="refresh-cw" size="14" className="me-1 align-middle" /> Reset DB
                      </Button>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row>
          {/* LEFT: AI Chat Terminal and Trace Flow */}
          <Col xl={6}>
            {/* Chat Terminal */}
            <Card className="mb-4" style={{ minHeight: "450px" }}>
              <CardHeader className="bg-light d-flex align-items-center justify-content-between">
                <h5 className="mb-0">💬 Terminal Tương Tác AI Agent ({activeDomain.toUpperCase()})</h5>
                <span className="text-muted fs-12">Domain: {activeDomain.toUpperCase()}</span>
              </CardHeader>
              <CardBody className="d-flex flex-column justify-content-between" style={{ height: "450px" }}>
                <div className="overflow-auto pe-2 mb-3" style={{ flexGrow: 1 }}>
                  {messages.map((m, idx) => (
                    <div key={idx} className={`d-flex mb-3 ${m.role === "user" ? "justify-content-end" : "justify-content-start"}`}>
                      <div className={`p-3 rounded-3 ${m.role === "user" ? "bg-primary text-white" : "bg-light text-dark"}`} style={{ maxWidth: "80%" }}>
                        <span className="fw-bold fs-12 d-block mb-1">{m.role === "user" ? "BẠN" : "AI AGENT"}</span>
                        <div className="fs-14" style={{ whiteSpace: "pre-line" }}>{m.content}</div>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="d-flex mb-3 justify-content-start">
                      <div className="bg-light p-3 rounded-3 text-dark" style={{ maxWidth: "80%" }}>
                        <span className="fw-bold fs-12 d-block mb-1">AI AGENT</span>
                        <div className="d-flex align-items-center">
                          <span className="spinner-border spinner-border-sm me-2 text-primary" role="status" />
                          <span className="fs-14">Đang xử lý luồng kiến trúc 9 bước...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <form onSubmit={handleSendMessage} className="d-flex gap-2">
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={
                      activeDomain === "sme"
                        ? "Hỏi về hủy đặt sân, lỗi hoàn tiền MoMo..."
                        : activeDomain === "education"
                        ? "Hỏi về sinh viên cảnh cáo học vụ, GPA học bổng..."
                        : "Hỏi về dịch sâu hại, độ ẩm đất, lịch tưới cây..."
                    }
                    disabled={loading}
                  />
                  <Button color="primary" type="submit" disabled={loading}>
                    <FeatherIcon icon="send" size="16" />
                  </Button>
                </form>
              </CardBody>
            </Card>

            {/* Trace Flow Visualization */}
            <Card>
              <CardHeader className="bg-light">
                <h5 className="mb-0">⚙️ Sơ đồ Trace Flow 9 Bước Kiến Trúc</h5>
              </CardHeader>
              <CardBody>
                <div className="d-flex flex-column gap-2 mb-4">
                  {stepsList.map((step) => {
                    const status = getStepStatus(step.key);
                    let color = "secondary";
                    let icon = "circle";
                    
                    if (status === "active") {
                      color = "success";
                      icon = "check-circle";
                    } else if (status === "blocked") {
                      color = "danger";
                      icon = "alert-octagon";
                    }
                    
                    const isSelected = selectedStep === step.key;

                    return (
                      <div
                        key={step.key}
                        onClick={() => setSelectedStep(step.key)}
                        className={`d-flex align-items-center justify-content-between p-2 border rounded-3 cursor-pointer ${isSelected ? "border-primary bg-light" : "border-light"}`}
                        style={{ cursor: "pointer", transition: "all 0.2s" }}
                      >
                        <div className="d-flex align-items-center gap-3">
                          <FeatherIcon icon={icon} className={`text-${color}`} />
                          <div>
                            <span className={`fw-semibold ${isSelected ? "text-primary" : ""}`}>{step.label}</span>
                            <div className="fs-12 text-muted">{step.desc}</div>
                          </div>
                        </div>
                        {telemetry && telemetry[step.key] && telemetry[step.key].duration_ms && (
                          <Badge color="light" className="text-dark">
                            {telemetry[step.key].duration_ms.toFixed(1)} ms
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Selected Step Detail Panel */}
                {selectedStep && (
                  <Card className="border border-primary-subtle bg-light-subtle">
                    <CardHeader className="bg-primary text-white py-2">
                      <h6 className="mb-0 text-white">Chi tiết bước: {stepsList.find(s => s.key === selectedStep)?.label}</h6>
                    </CardHeader>
                    <CardBody className="fs-13">
                      <Row>
                        <Col md={6}>
                          <div className="fw-bold mb-1">Dữ liệu chạy thực (Telemetry logs):</div>
                          <pre className="bg-dark text-success p-2 rounded" style={{ maxHeight: "150px", overflow: "auto" }}>
                            {telemetry && telemetry[selectedStep] 
                              ? JSON.stringify(telemetry[selectedStep], null, 2) 
                              : "Không có dữ liệu lượt chạy này."}
                          </pre>
                        </Col>
                        <Col md={6}>
                          <div className="fw-bold mb-1">Blueprint Code (Python):</div>
                          <pre className="bg-dark text-white p-2 rounded" style={{ maxHeight: "150px", overflow: "auto" }}>
                            {blueprints[selectedStep]}
                          </pre>
                        </Col>
                      </Row>
                    </CardBody>
                  </Card>
                )}
              </CardBody>
            </Card>
          </Col>

          {/* RIGHT: Mock Database view & HITL queue */}
          <Col xl={6}>
            {/* Database & State view */}
            <Card className="mb-4">
              <CardHeader className="bg-light d-flex align-items-center justify-content-between">
                <h5 className="mb-0">🗄️ CSDL Vận Hành (Lĩnh vực: {activeDomain.toUpperCase()})</h5>
                {activeDomain === "sme" && dbState?.wallet && (
                  <Badge color="info" className="fs-13">
                    Ví ảo: {dbState.wallet.balance.toLocaleString()} {dbState.wallet.currency}
                  </Badge>
                )}
              </CardHeader>
              <CardBody>
                {/* Service Status */}
                <h6 className="text-muted mb-2">Trạng thái dịch vụ backend:</h6>
                <Row className="mb-4 gap-2 px-3">
                  {dbState && Object.entries(dbState.services).map(([name, info]) => (
                    <Col key={name} className="border p-2 rounded-3 bg-light">
                      <div className="d-flex align-items-center justify-content-between mb-1">
                        <span className="fw-bold text-uppercase fs-12">{name}</span>
                        <Badge color={info.status === "operational" ? "success" : "warning"}>
                          {info.status}
                        </Badge>
                      </div>
                      <div className="fs-11 text-muted text-truncate">{info.log}</div>
                    </Col>
                  ))}
                </Row>

                {/* --- SME RENDER --- */}
                {activeDomain === "sme" && (
                  <>
                    <h6 className="text-muted mb-2">Thông tin Booking Sân:</h6>
                    <Table responsive size="sm" className="mb-4 align-middle">
                      <thead>
                        <tr>
                          <th>Booking ID</th>
                          <th>Môn</th>
                          <th>Sân</th>
                          <th>Thời gian</th>
                          <th>Giá</th>
                          <th>Trạng thái</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.bookings?.map((b) => (
                          <tr key={b.booking_id}>
                            <td className="fw-bold">{b.booking_id}</td>
                            <td>{b.sport}</td>
                            <td>{b.court}</td>
                            <td>{b.date} {b.time}</td>
                            <td>{b.amount.toLocaleString()}đ</td>
                            <td>
                              <Badge color={b.status === "Paid" ? "success" : "danger"}>
                                {b.status}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>

                    <h6 className="text-muted mb-2">Vé Hỗ Trợ (Support Tickets):</h6>
                    <Table responsive size="sm" className="align-middle">
                      <thead>
                        <tr>
                          <th>Ticket ID</th>
                          <th>Tiêu đề</th>
                          <th>Bộ phận</th>
                          <th>Độ ưu tiên</th>
                          <th>Trạng thái</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.tickets?.map((t) => (
                          <tr key={t.ticket_id}>
                            <td className="fw-bold">{t.ticket_id}</td>
                            <td>{t.title}</td>
                            <td>{t.service}</td>
                            <td>
                              <Badge color={t.priority === "High" ? "danger" : "warning"}>
                                {t.priority}
                              </Badge>
                            </td>
                            <td>
                              <Badge color="info">{t.status}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </>
                )}

                {/* --- EDUCATION RENDER --- */}
                {activeDomain === "education" && (
                  <>
                    <h6 className="text-muted mb-2">Danh sách Sinh viên:</h6>
                    <Table responsive size="sm" className="mb-4 align-middle">
                      <thead>
                        <tr>
                          <th>MSSV</th>
                          <th>Họ và Tên</th>
                          <th>Ngành học</th>
                          <th>GPA</th>
                          <th>Chuyên cần</th>
                          <th>Midterm</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.students?.map((s) => (
                          <tr key={s.student_id}>
                            <td className="fw-bold">{s.student_id}</td>
                            <td>{s.name}</td>
                            <td>{s.major}</td>
                            <td>{s.prior_gpa}</td>
                            <td>
                              <Badge color={s.attendance_rate < 0.8 ? "danger" : "success"}>
                                {(s.attendance_rate * 100).toFixed(0)}%
                              </Badge>
                            </td>
                            <td>
                              <Badge color={s.midterm_grade < 5.0 ? "danger" : "success"}>
                                {s.midterm_grade}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>

                    <h6 className="text-muted mb-2">Nhật ký Can thiệp học vụ:</h6>
                    <Table responsive size="sm" className="align-middle">
                      <thead>
                        <tr>
                          <th>Mã Log</th>
                          <th>MSSV</th>
                          <th>Hình thức</th>
                          <th>Ghi chú</th>
                          <th>Trạng thái</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.intervention_logs?.map((l) => (
                          <tr key={l.log_id}>
                            <td className="fw-bold">{l.log_id}</td>
                            <td>{l.student_id}</td>
                            <td>{l.intervention_type}</td>
                            <td>{l.note}</td>
                            <td>
                              <Badge color="info">{l.status}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </>
                )}

                {/* --- AGRICULTURE RENDER --- */}
                {activeDomain === "agriculture" && (
                  <>
                    <h6 className="text-muted mb-2">Danh sách Lô vườn (Plots):</h6>
                    <Table responsive size="sm" className="mb-4 align-middle">
                      <thead>
                        <tr>
                          <th>Mã Lô</th>
                          <th>Tên Lô</th>
                          <th>Cây trồng</th>
                          <th>Tổn hại lá</th>
                          <th>Độ ẩm đất</th>
                          <th>Lần phun cuối</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.farms?.map((f) => (
                          <tr key={f.farm_id}>
                            <td className="fw-bold">{f.farm_id}</td>
                            <td>{f.name}</td>
                            <td>{f.crop_type}</td>
                            <td>
                              <Badge color={f.leaf_damage_percent > 20.0 ? "danger" : "success"}>
                                {f.leaf_damage_percent}%
                              </Badge>
                            </td>
                            <td>{f.soil_moisture}%</td>
                            <td>{f.days_since_last_treatment} ngày trước</td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>

                    <h6 className="text-muted mb-2">Nhật ký Xử lý bảo vệ thực vật:</h6>
                    <Table responsive size="sm" className="align-middle">
                      <thead>
                        <tr>
                          <th>Mã Log</th>
                          <th>Mã Cây</th>
                          <th>Loại tác vụ</th>
                          <th>Ghi chú nồng độ</th>
                          <th>Trạng thái</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dbState?.treatment_logs?.map((l) => (
                          <tr key={l.log_id}>
                            <td className="fw-bold">{l.log_id}</td>
                            <td>{l.crop_id}</td>
                            <td>{l.treatment_type}</td>
                            <td>{l.notes}</td>
                            <td>
                              <Badge color="success">{l.status}</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </>
                )}
              </CardBody>
            </Card>

            {/* Human-in-the-Loop Approvals Queue */}
            <Card>
              <CardHeader className="bg-warning-subtle text-warning-emphasis">
                <h5 className="mb-0 text-warning-emphasis">⏳ Human-in-the-Loop Approval Queue (Yêu cầu chờ duyệt)</h5>
              </CardHeader>
              <CardBody>
                {dbState?.pending_approvals && dbState.pending_approvals.filter(a => a.status === "Pending").length === 0 ? (
                  <div className="text-center text-muted py-4">Không có giao dịch/hành động nào cần phê duyệt vào lúc này.</div>
                ) : (
                  dbState?.pending_approvals?.filter(a => a.status === "Pending").map((a) => (
                    <div key={a.approval_id} className="border border-warning p-3 rounded-3 mb-3 bg-warning-subtle-light">
                      <div className="d-flex align-items-center justify-content-between mb-2">
                        <span className="fw-bold text-danger fs-14">⚠️ YÊU CẦU DUYỆT HÀNH ĐỘNG RỦI RO</span>
                        <Badge color="warning">{a.approval_id}</Badge>
                      </div>
                      <div className="fs-13 mb-3">
                        <div><strong>Hành động:</strong> {a.action_type}</div>
                        {activeDomain === "sme" && (
                          <>
                            <div><strong>Mã đặt chỗ:</strong> {a.details.booking_id}</div>
                            <div><strong>Số tiền hoàn:</strong> {a.details.refund_amount?.toLocaleString()} VND</div>
                          </>
                        )}
                        {activeDomain === "education" && (
                          <>
                            <div><strong>Mã sinh viên:</strong> {a.details.student_id}</div>
                            <div><strong>Nghiệp vụ:</strong> {a.details.issue}</div>
                          </>
                        )}
                        {activeDomain === "agriculture" && (
                          <>
                            <div><strong>Mã Lô cây:</strong> {a.details.crop_id}</div>
                            <div><strong>Thuốc đề xuất:</strong> {a.details.chemical}</div>
                          </>
                        )}
                        <div className="mt-1 text-muted"><strong>Query người dùng:</strong> "{a.details.user_query}"</div>
                        <div className="mt-1">
                          <strong>Phân loại rủi ro (PyTorch): </strong>
                          <Badge color={a.details.risk_level === "high" ? "danger" : "warning"}>
                            {a.details.risk_level?.toUpperCase()} (Priority: {a.details.priority?.toFixed(2)})
                          </Badge>
                        </div>
                      </div>
                      <div className="d-flex gap-2">
                        <Button color="success" size="sm" onClick={() => handleApprove(a.approval_id)}>
                          Approve (Đồng ý thực thi)
                        </Button>
                        <Button color="danger" size="sm" onClick={() => handleReject(a.approval_id)}>
                          Reject (Từ chối)
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
}
