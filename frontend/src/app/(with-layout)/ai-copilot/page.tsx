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

interface Approval {
  approval_id: string;
  action_type: string;
  details: Record<str, any>;
  status: string;
}

interface DbState {
  wallet: { balance: number; currency: string };
  services: Record<str, ServiceInfo>;
  bookings: Booking[];
  tickets: Ticket[];
  pending_approvals?: Approval[];
}

interface TraceStep {
  name: string;
  duration_ms?: number;
  [key: string]: any;
}

export default function AICopilotDashboard() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    { role: "assistant", content: "Xin chào! Tôi là Trợ lý vận hành AI-native. Hãy thử hỏi về chính sách hủy sân, kiểm tra tình trạng cổng thanh toán hoặc yêu cầu hủy đặt sân!" }
  ]);
  const [telemetry, setTelemetry] = useState<Record<string, any> | null>(null);
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [dbState, setDbState] = useState<DbState | null>(null);
  const [backendStatus, setBackendStatus] = useState<"connecting" | "online" | "offline">("connecting");
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = "http://localhost:8000";

  // Fetch db state and approvals
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

  useEffect(() => {
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
          // Auto select first step
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
      setMessages([{ role: "assistant", content: "Cơ sở dữ liệu đã được đặt lại về mặc định." }]);
      setTelemetry(null);
      setSelectedStep(null);
    } catch (err) {
      console.error(err);
    }
  };

  // Trace steps layout
  const stepsList = [
    { key: "step_1_pii", label: "1. PII Scan", desc: "Quét thông tin cá nhân nhạy cảm & che giấu." },
    { key: "step_2_input_safety", label: "2. Input Safety", desc: "Lọc prompt injection & SQL injection." },
    { key: "step_3_router", label: "3. Model Router", desc: "Định tuyến Cache/FAQ/Agent." },
    { key: "step_4_rag", label: "4. CUDA RAG", desc: "Tìm kiếm tri thức chính sách Vector DB." },
    { key: "step_5_planner", label: "5. Agent Planner", desc: "Suy nghĩ & lên kế hoạch ReAct." },
    { key: "step_6_executor", label: "6. Tool Executor", desc: "Chạy API nghiệp vụ & CSDL." },
    { key: "step_7_hitl", label: "7. Human Approval", desc: "Duyệt tác vụ tài chính rủi ro cao." },
    { key: "step_8_output_safety", label: "8. Output Guardrail", desc: "Quét ảo tưởng (Hallucination Risk)." },
    { key: "step_9_dispatcher", label: "9. Smart Dispatch", desc: "Phục hồi PII & đóng gói phản hồi." },
  ];

  const getStepStatus = (key: string) => {
    if (!telemetry || !telemetry[key]) return "inactive";
    const data = telemetry[key];
    if (data.is_blocked || data.status === "Blocked") return "blocked";
    if (data.triggered || data.docs_found > 0 || data.steps?.length > 0 || data.route || data.success || data.total_duration_ms || data.redacted_query) return "active";
    return "inactive";
  };

  // Helper code blueprint mapping
  const blueprints: Record<string, string> = {
    step_1_pii: `def scan_and_redact(text):\n  # Che SĐT và Email Việt Nam\n  text = re.sub(r'0\\d{9}', '[REDACTED_PHONE]', text)\n  return text`,
    step_2_input_safety: `def check_injection(text):\n  if "bỏ qua các lệnh trước" in text.lower():\n    return Blocked(score=1.0)\n  return Safe(score=0.0)`,
    step_3_router: `def route(query):\n  if query in faq_cache:\n    return Route.CACHE\n  if "hủy" in query:\n    return Route.AGENT\n  return Route.FAQ`,
    step_4_rag: `def cosine_similarity(q, d):\n  return np.dot(q, d) / (norm(q) * norm(d))\n# Query direct on CUDA PyTorch/SentenceTransformers`,
    step_5_planner: `Prompt: Use ReAct pattern.\\nFormat: Thought -> Action -> Observation -> Final Answer`,
    step_6_executor: `@tool_registry.register()\\ndef create_support_ticket(title, service):\\n  # DB CRUD Write`,
    step_7_hitl: `if amount_refund > 500000:\\n  create_pending_approval(action, amount)`,
    step_8_output_safety: `def check_hallucination(resp, docs):\\n  # Jaccard overlap on non-stop words\\n  return overlaps / response_len`,
    step_9_dispatcher: `def dispatch(text, mapping):\\n  return restore_pii(text, mapping)`,
  };

  return (
    <div className="page-content" style={{ padding: "80px 20px 20px 20px" }}>
      <Container fluid>
        {/* Backend offline alert */}
        {backendStatus === "offline" && (
          <Alert color="danger" className="d-flex align-items-center">
            <FeatherIcon icon="alert-triangle" className="me-2" />
            <div>
              <strong>FastAPI Backend offline!</strong> Vui lòng chạy lệnh <code>python main.py</code> trong thư mục <code>backend</code> để khởi động API (Cổng 8000).
            </div>
          </Alert>
        )}

        {/* Header Telemetry */}
        <Row className="mb-4">
          <Col lg={12}>
            <Card className="bg-dark text-white border-0 overflow-hidden" style={{ borderRadius: "12px" }}>
              <CardBody className="p-4">
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
                  <div>
                    <h4 className="text-white mb-1">
                      <Badge color="success" className="me-2 align-middle">Live</Badge>
                      Vietnam AI Challenge - Operations Copilot Cockpit
                    </h4>
                    <p className="text-white-50 mb-0">Hệ thống giám sát vận hành AI-Native tích hợp Guardrails & HITL</p>
                  </div>
                  <div className="d-flex align-items-center gap-4 text-white-50 flex-wrap">
                    <div className="d-flex align-items-center gap-2">
                      <FeatherIcon icon="cpu" className="text-success" />
                      <div>
                        <div className="fs-12 text-muted">GPU MONITOR (Local)</div>
                        <div className="text-white fw-bold fs-14">RTX 3070 CUDA (39°C)</div>
                      </div>
                    </div>
                    <div className="d-flex align-items-center gap-2">
                      <FeatherIcon icon="activity" className="text-info" />
                      <div>
                        <div className="fs-12 text-muted">TOTAL LATENCY</div>
                        <div className="text-white fw-bold fs-14">
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
          {/* LEFT: AI Chat and Trace Flow */}
          <Col xl={6}>
            {/* Chat Terminal */}
            <Card className="mb-4" style={{ minHeight: "450px" }}>
              <CardHeader className="bg-light d-flex align-items-center justify-content-between">
                <h5 className="mb-0">💬 Terminal Tương Tác AI Agent</h5>
                <span className="text-muted fs-12">Model: {settings.MODEL_NAME}</span>
              </CardHeader>
              <CardBody className="d-flex flex-column justify-content-between" style={{ height: "450px" }}>
                <div className="overflow-auto pe-2 mb-3" style={{ flexGrow: 1 }}>
                  {messages.map((m, idx) => (
                    <div key={idx} className={`d-flex mb-3 ${m.role === "user" ? "justify-content-end" : "justify-content-start"}`}>
                      <div className={`p-3 rounded-3 max-width-70 ${m.role === "user" ? "bg-primary text-white" : "bg-light text-dark"}`} style={{ maxWidth: "80%" }}>
                        <span className="fw-bold fs-12 d-block mb-1">{m.role === "user" ? "BẠN" : "AI AGENT"}</span>
                        <div className="fs-14" style={{ whiteSpace: "pre-line" }}>{m.content}</div>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="d-flex mb-3 justify-content-start">
                      <div className="bg-light p-3 rounded-3">
                        <span className="fw-bold fs-12 d-block mb-1">AI AGENT</span>
                        <span className="spinner-border spinner-border-sm me-2 text-primary" role="status" />
                        <span className="fs-14 text-muted">Đang xử lý luồng kiến trúc 9 bước...</span>
                      </div>
                    </div>
                  )}
                </div>
                <form onSubmit={handleSendMessage} className="d-flex gap-2">
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Nhập yêu cầu (Ví dụ: 'Nếu tôi hủy sân trước 7 tiếng có được hoàn tiền không?')"
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
                        className={`d-flex align-items-center justify-content-between p-2 border rounded-3 cursor-pointer transition-all ${isSelected ? "border-primary bg-light" : "border-light"}`}
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

          {/* RIGHT: Mock Database tables & HITL approvals */}
          <Col xl={6}>
            {/* Database & State view */}
            <Card className="mb-4">
              <CardHeader className="bg-light d-flex align-items-center justify-content-between">
                <h5 className="mb-0">🗄️ CSDL Vận Hành (Simulated Database)</h5>
                {dbState && (
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

                {/* Bookings */}
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
                    {dbState?.bookings.map((b) => (
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

                {/* Tickets */}
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
                    {dbState?.tickets.map((t) => (
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
              </CardBody>
            </Card>

            {/* Human-in-the-Loop Approvals queue */}
            <Card>
              <CardHeader className="bg-warning-subtle text-warning-emphasis">
                <h5 className="mb-0 text-warning-emphasis">⏳ Human-in-the-Loop Approval Queue (Yêu cầu cần Admin duyệt)</h5>
              </CardHeader>
              <CardBody>
                {dbState?.pending_approvals && dbState.pending_approvals.filter(a => a.status === "Pending").length === 0 ? (
                  <div className="text-center text-muted py-4">Không có giao dịch/hành động nào cần phê duyệt vào lúc này.</div>
                ) : (
                  dbState?.pending_approvals?.filter(a => a.status === "Pending").map((a) => (
                    <div key={a.approval_id} className="border border-warning p-3 rounded-3 mb-3 bg-warning-subtle-light">
                      <div className="d-flex align-items-center justify-content-between mb-2">
                        <span className="fw-bold text-danger fs-14">⚠️ YÊU CẦU HOÀN TIỀN KHẨN CẤP</span>
                        <Badge color="warning">{a.approval_id}</Badge>
                      </div>
                      <div className="fs-13 mb-3">
                        <div><strong>Hành động:</strong> {a.action_type}</div>
                        <div><strong>Mã đặt sân:</strong> {a.details.booking_id}</div>
                        <div><strong>Số tiền hoàn:</strong> {a.details.refund_amount.toLocaleString()} VND</div>
                        <div className="text-muted"><strong>Query khách hàng:</strong> "{a.details.user_query}"</div>
                      </div>
                      <div className="d-flex gap-2">
                        <Button color="success" size="sm" onClick={() => handleApprove(a.approval_id)}>
                          Approve (Đồng ý hoàn tiền)
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
