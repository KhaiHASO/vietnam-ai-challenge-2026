"use client";

import React, { useState } from "react";
import {
  Row,
  Col,
  Card,
  CardBody,
  Button,
  Badge,
  Progress,
} from "reactstrap";
import Link from "next/link";

type Step = 1 | 2 | 3 | 4;

const crops = [
  { value: "ot", label: "🌶️ Ớt" },
  { value: "ca-chua", label: "🍅 Cà chua" },
  { value: "dua-leo", label: "🥒 Dưa leo" },
  { value: "cai-xanh", label: "🥬 Cải xanh" },
  { value: "lua", label: "🌾 Lúa" },
  { value: "ngo", label: "🌽 Ngô" },
];

const farms = [
  { value: "vuon-ot", label: "Vườn ớt Trảng Bom" },
  { value: "ruong-ca", label: "Ruộng cà Long Thành" },
  { value: "vuon-dua", label: "Vườn dưa Nhơn Trạch" },
];

const agentSteps = [
  {
    id: "vision",
    agent: "Vision Agent",
    icon: "ri-eye-line",
    color: "#7c3aed",
    message: "Phát hiện đốm lá màu nâu, hình tròn, lõm ở tâm. Nghi bệnh nấm — Anthracnose 74%.",
    done: true,
  },
  {
    id: "symptom",
    agent: "Symptom Agent",
    icon: "ri-questionnaire-line",
    color: "#2563eb",
    message: "Triệu chứng xuất hiện sau mưa hay sau phun thuốc? Có lan sang quả chưa?",
    done: true,
    isQuestion: true,
    answer: "Sau đợt mưa 3 ngày liên tiếp. Đã thấy đốm trên 2-3 quả non.",
  },
  {
    id: "context",
    agent: "Context Agent",
    icon: "ri-cloud-line",
    color: "#0891b2",
    message: "Thời tiết Trảng Bom 3 ngày: mưa, độ ẩm 85-92%. Điều kiện thuận lợi cho nấm Colletotrichum.",
    done: true,
  },
  {
    id: "reasoning",
    agent: "Reasoning Agent",
    icon: "ri-brain-line",
    color: "#059669",
    message: "Tổng hợp: Hình ảnh (74%) + Triệu chứng + Thời tiết → Xác suất Thán thư tăng lên 89%.",
    done: true,
  },
  {
    id: "safety",
    agent: "Safety Agent",
    icon: "ri-shield-check-line",
    color: "#d97706",
    message: "⚠️ Không khuyến nghị phun thuốc ngay. Áp dụng IPM: tỉa lá bệnh trước, giảm ẩm, theo dõi 48h.",
    done: true,
  },
  {
    id: "diary",
    agent: "Diary Agent",
    icon: "ri-book-2-line",
    color: "#6b7280",
    message: "Đã lưu ca bệnh #2026-0704-001 vào nhật ký. Đặt nhắc kiểm tra lại sau 48h.",
    done: true,
  },
];

export default function DiagnosisNew() {
  const [step, setStep] = useState<Step>(1);
  const [selectedCrop, setSelectedCrop] = useState("");
  const [selectedFarm, setSelectedFarm] = useState("");
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [symptomAnswer, setSymptomAnswer] = useState("");

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0].name);
    }
  };

  const runAnalysis = () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    let prog = 0;
    const interval = setInterval(() => {
      prog += Math.random() * 18 + 5;
      if (prog >= 100) {
        prog = 100;
        clearInterval(interval);
        setTimeout(() => {
          setIsAnalyzing(false);
          setStep(3);
        }, 600);
      }
      setAnalysisProgress(Math.round(prog));
    }, 200);
  };

  const steps = [
    { num: 1, label: "Thông tin cây" },
    { num: 2, label: "Upload ảnh" },
    { num: 3, label: "AI phân tích" },
    { num: 4, label: "Kết quả" },
  ];

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center gap-3">
              <Link href="/dashboard">
                <Button color="light" size="sm" className="btn-icon" id="btn-back-dashboard">
                  <i className="ri-arrow-left-line"></i>
                </Button>
              </Link>
              <div>
                <h4 className="mb-0 fw-semibold">
                  <i className="ri-microscope-line text-success me-2"></i>
                  Chẩn đoán mới
                </h4>
                <p className="text-muted mb-0 fs-13">
                  AI phân tích ảnh + hỏi triệu chứng → chẩn đoán chính xác
                </p>
              </div>
            </div>
          </Col>
        </Row>

        {/* Step Indicator */}
        <Row className="mb-4">
          <Col>
            <div className="d-flex align-items-center gap-0">
              {steps.map((s, idx) => (
                <React.Fragment key={s.num}>
                  <div className="d-flex flex-column align-items-center">
                    <div
                      className={`d-flex align-items-center justify-content-center rounded-circle fw-bold fs-14`}
                      style={{
                        width: 36,
                        height: 36,
                        background:
                          step > s.num
                            ? "#2dce89"
                            : step === s.num
                              ? "#405189"
                              : "var(--vz-border-color)",
                        color: step >= s.num ? "white" : "var(--vz-body-color)",
                        transition: "all 0.3s",
                      }}
                    >
                      {step > s.num ? (
                        <i className="ri-check-line"></i>
                      ) : (
                        s.num
                      )}
                    </div>
                    <span
                      className="fs-11 mt-1"
                      style={{
                        color:
                          step === s.num
                            ? "#405189"
                            : "var(--vz-text-muted)",
                        fontWeight: step === s.num ? 600 : 400,
                      }}
                    >
                      {s.label}
                    </span>
                  </div>
                  {idx < steps.length - 1 && (
                    <div
                      style={{
                        flex: 1,
                        height: 2,
                        background:
                          step > s.num ? "#2dce89" : "var(--vz-border-color)",
                        marginBottom: 18,
                        transition: "all 0.3s",
                      }}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>
          </Col>
        </Row>

        {/* Step 1: Crop & Farm Selection */}
        {step === 1 && (
          <Row className="justify-content-center">
            <Col xl={7}>
              <Card>
                <CardBody className="p-4">
                  <h5 className="fw-semibold mb-4">
                    Bước 1: Chọn cây trồng & vườn
                  </h5>
                  <div className="mb-4">
                    <label className="form-label fw-medium">
                      🌱 Loại cây trồng
                    </label>
                    <div className="d-flex flex-wrap gap-2">
                      {crops.map((c) => (
                        <button
                          key={c.value}
                          id={`crop-${c.value}`}
                          onClick={() => setSelectedCrop(c.value)}
                          className="btn"
                          style={{
                            border: `2px solid ${selectedCrop === c.value ? "#2dce89" : "var(--vz-border-color)"}`,
                            background:
                              selectedCrop === c.value
                                ? "rgba(45,206,137,0.1)"
                                : "transparent",
                            color:
                              selectedCrop === c.value
                                ? "#2dce89"
                                : "var(--vz-body-color)",
                            fontWeight: selectedCrop === c.value ? 600 : 400,
                            transition: "all 0.2s",
                          }}
                        >
                          {c.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="mb-4">
                    <label className="form-label fw-medium">
                      📍 Vườn canh tác
                    </label>
                    <select
                      id="select-farm"
                      className="form-select"
                      value={selectedFarm}
                      onChange={(e) => setSelectedFarm(e.target.value)}
                    >
                      <option value="">Chọn vườn...</option>
                      {farms.map((f) => (
                        <option key={f.value} value={f.value}>
                          {f.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="d-flex justify-content-end">
                    <Button
                      color="success"
                      id="btn-step1-next"
                      disabled={!selectedCrop || !selectedFarm}
                      onClick={() => setStep(2)}
                    >
                      Tiếp theo
                      <i className="ri-arrow-right-line ms-2"></i>
                    </Button>
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 2: Image Upload */}
        {step === 2 && (
          <Row className="justify-content-center">
            <Col xl={7}>
              <Card>
                <CardBody className="p-4">
                  <h5 className="fw-semibold mb-1">Bước 2: Chụp / Upload ảnh</h5>
                  <p className="text-muted fs-13 mb-4">
                    Chụp ảnh rõ nét phần lá/quả bị bệnh trong điều kiện ánh sáng tốt
                  </p>
                  <label
                    htmlFor="file-upload"
                    id="drop-zone"
                    className="d-flex flex-column align-items-center justify-content-center p-5 rounded"
                    style={{
                      border: "2px dashed #2dce89",
                      background: "rgba(45,206,137,0.04)",
                      cursor: "pointer",
                      transition: "background 0.2s",
                      minHeight: 220,
                    }}
                  >
                    {uploadedFile ? (
                      <div className="text-center">
                        <div
                          style={{
                            width: 80,
                            height: 80,
                            background: "rgba(45,206,137,0.1)",
                            borderRadius: 12,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            margin: "0 auto 16px",
                          }}
                        >
                          <i className="ri-image-2-line text-success fs-36"></i>
                        </div>
                        <p className="fw-semibold text-success mb-1">
                          {uploadedFile}
                        </p>
                        <p className="text-muted fs-12 mb-0">
                          Nhấn để thay đổi ảnh
                        </p>
                      </div>
                    ) : (
                      <div className="text-center">
                        <i className="ri-upload-cloud-2-line fs-48 text-success mb-3 d-block"></i>
                        <p className="fw-semibold mb-1">
                          Kéo thả ảnh vào đây
                        </p>
                        <p className="text-muted fs-13 mb-0">
                          hoặc nhấn để chọn ảnh · JPG, PNG, HEIC
                        </p>
                      </div>
                    )}
                    <input
                      id="file-upload"
                      type="file"
                      accept="image/*"
                      className="d-none"
                      onChange={handleUpload}
                    />
                  </label>
                  <div className="mt-3 p-3 rounded" style={{ background: "rgba(255,193,7,0.08)", border: "1px solid rgba(255,193,7,0.3)" }}>
                    <p className="mb-0 fs-13 text-warning">
                      <i className="ri-lightbulb-flash-line me-2"></i>
                      <strong>Mẹo:</strong> Chụp từ khoảng cách 20–30cm, đủ ánh sáng, tập trung vào vùng bị bệnh
                    </p>
                  </div>
                  <div className="d-flex justify-content-between mt-4">
                    <Button color="light" id="btn-step2-back" onClick={() => setStep(1)}>
                      <i className="ri-arrow-left-line me-2"></i>Quay lại
                    </Button>
                    {isAnalyzing ? (
                      <div className="d-flex flex-column align-items-end gap-2" style={{ minWidth: 200 }}>
                        <span className="text-muted fs-13">
                          Đang phân tích AI... {analysisProgress}%
                        </span>
                        <Progress value={analysisProgress} color="success" style={{ width: 200, height: 8 }} />
                      </div>
                    ) : (
                      <Button
                        color="success"
                        id="btn-analyze"
                        onClick={() => {
                          setUploadedFile("anh_ot_benh_mau.jpg");
                          runAnalysis();
                        }}
                      >
                        <i className="ri-cpu-line me-2"></i>
                        Phân tích AI
                      </Button>
                    )}
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 3: Agent Analysis */}
        {step === 3 && (
          <Row className="justify-content-center">
            <Col xl={8}>
              <Card>
                <CardBody className="p-4">
                  <h5 className="fw-semibold mb-1">Bước 3: AI Agent đang phân tích</h5>
                  <p className="text-muted fs-13 mb-4">
                    Multi-agent system xử lý hình ảnh → hỏi triệu chứng → kết luận
                  </p>
                  <div className="d-flex flex-column gap-3">
                    {agentSteps.map((ag) => (
                      <div
                        key={ag.id}
                        id={`agent-${ag.id}`}
                        className="d-flex gap-3 p-3 rounded"
                        style={{
                          border: `1px solid ${ag.color}30`,
                          background: `${ag.color}08`,
                        }}
                      >
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: 8,
                            background: ag.color,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <i className={`${ag.icon} text-white`}></i>
                        </div>
                        <div className="flex-grow-1">
                          <p className="mb-1 fw-semibold fs-13" style={{ color: ag.color }}>
                            {ag.agent}
                          </p>
                          <p className="mb-0 fs-13">{ag.message}</p>
                          {ag.isQuestion && ag.answer && (
                            <div className="mt-2 p-2 rounded" style={{ background: "rgba(0,0,0,0.04)" }}>
                              <p className="mb-0 fs-12 text-muted">
                                <i className="ri-user-voice-line me-1"></i>
                                Nông dân trả lời: <em>"{ag.answer}"</em>
                              </p>
                            </div>
                          )}
                        </div>
                        <i className="ri-check-double-line text-success fs-18 flex-shrink-0"></i>
                      </div>
                    ))}
                  </div>
                  <div className="d-flex justify-content-end mt-4">
                    <Button color="success" id="btn-view-result" onClick={() => setStep(4)}>
                      Xem kết quả chẩn đoán
                      <i className="ri-arrow-right-line ms-2"></i>
                    </Button>
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 4: Result */}
        {step === 4 && (
          <Row className="justify-content-center">
            <Col xl={9}>
              <Row>
                <Col md={6} className="mb-3">
                  <Card className="h-100">
                    <CardBody className="p-4">
                      <div className="d-flex align-items-center gap-2 mb-3">
                        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444" }}></div>
                        <h6 className="fw-bold mb-0 text-danger">⚠️ Kết quả chẩn đoán</h6>
                      </div>
                      <h4 className="fw-bold mb-1">Thán thư (Anthracnose)</h4>
                      <p className="text-muted fs-13 mb-3">
                        Tác nhân: <strong>Colletotrichum capsici</strong> · Nhóm: Bệnh nấm
                      </p>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between mb-1">
                          <span className="fs-13">Độ tin cậy AI</span>
                          <strong className="text-danger">89%</strong>
                        </div>
                        <Progress value={89} color="danger" style={{ height: 10, borderRadius: 6 }} />
                      </div>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between mb-1">
                          <span className="fs-13">Bệnh thứ hai có thể</span>
                          <span className="text-muted">Đốm lá vi khuẩn — 8%</span>
                        </div>
                        <Progress value={8} color="warning" style={{ height: 6, borderRadius: 6 }} />
                      </div>
                      <hr />
                      <div>
                        <p className="fw-semibold fs-13 mb-2">📋 Triệu chứng phát hiện:</p>
                        <ul className="fs-13 text-muted ps-3 mb-0">
                          <li>Đốm nâu hình tròn, viền vàng trên lá</li>
                          <li>Vết lõm ở tâm đốm bệnh</li>
                          <li>Đốm lan rộng trên quả non</li>
                          <li>Xuất hiện sau đợt mưa dài</li>
                        </ul>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
                <Col md={6} className="mb-3">
                  <Card className="h-100">
                    <CardBody className="p-4">
                      <h6 className="fw-semibold mb-3">
                        <i className="ri-shield-check-line text-success me-2"></i>
                        Khuyến nghị IPM
                      </h6>
                      <div className="d-flex flex-column gap-3">
                        <div className="p-3 rounded" style={{ background: "rgba(45,206,137,0.08)", border: "1px solid rgba(45,206,137,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-success">✅ Ngay lập tức</p>
                          <ul className="fs-13 mb-0 ps-3">
                            <li>Tỉa và tiêu hủy lá, quả bệnh</li>
                            <li>Giảm tưới, cải thiện thông gió</li>
                            <li>Không dùng phân đạm cao</li>
                          </ul>
                        </div>
                        <div className="p-3 rounded" style={{ background: "rgba(255,193,7,0.08)", border: "1px solid rgba(255,193,7,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-warning">⏱️ Sau 48h theo dõi</p>
                          <ul className="fs-13 mb-0 ps-3">
                            <li>Nếu lan rộng: dùng Copper Hydroxide</li>
                            <li>Theo nguyên tắc 4 đúng</li>
                          </ul>
                        </div>
                        <div className="p-3 rounded" style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-danger">🔬 Cần chuyên gia nếu</p>
                          <ul className="fs-13 mb-0 ps-3">
                            <li>Bệnh lan &gt;30% diện tích</li>
                            <li>Không giảm sau 5–7 ngày</li>
                          </ul>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              </Row>
              <Row>
                <Col>
                  <Card>
                    <CardBody className="p-4">
                      <div className="d-flex gap-3 flex-wrap">
                        <Button color="success" id="btn-save-case" className="d-flex align-items-center gap-2">
                          <i className="ri-save-line"></i>Lưu ca bệnh
                        </Button>
                        <Button color="warning" id="btn-set-followup" className="d-flex align-items-center gap-2">
                          <i className="ri-notification-3-line"></i>Đặt nhắc theo dõi 48h
                        </Button>
                        <Link href="/diagnosis/history">
                          <Button color="light" id="btn-view-history" className="d-flex align-items-center gap-2">
                            <i className="ri-history-line"></i>Xem lịch sử
                          </Button>
                        </Link>
                        <Link href="/expert/review">
                          <Button color="light" id="btn-send-expert" className="d-flex align-items-center gap-2">
                            <i className="ri-stethoscope-line"></i>Gửi chuyên gia
                          </Button>
                        </Link>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              </Row>
            </Col>
          </Row>
        )}
      </div>
    </div>
  );
}
