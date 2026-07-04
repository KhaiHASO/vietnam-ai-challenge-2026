"use client";

import React, { useState } from "react";
import { Row, Col, Card, CardBody, Badge, Button, Progress } from "reactstrap";
import Link from "next/link";

const followUpCases = [
  {
    id: "fu-001",
    emoji: "🌶️",
    crop: "Ớt",
    farm: "Vườn ớt Trảng Bom",
    disease: "Thán thư (Anthracnose)",
    confidence: 89,
    reason: "camera",
    reasonLabel: "Chụp lại sau 48h",
    deadline: "06/07/2026 08:00",
    hoursLeft: 14,
    severity: "high",
    notes: "Đốm bệnh có xu hướng lan rộng, cần theo dõi sát",
    date: "04/07/2026",
  },
  {
    id: "fu-002",
    emoji: "🌶️",
    crop: "Ớt",
    farm: "Vườn ớt Trảng Bom",
    disease: "Héo xanh vi khuẩn",
    confidence: 78,
    reason: "spreading",
    reasonLabel: "Bệnh đang lan rộng",
    deadline: "05/07/2026 14:00",
    hoursLeft: -2,
    severity: "critical",
    notes: "Phát hiện thêm 3 cây mới có triệu chứng tương tự",
    date: "30/06/2026",
  },
  {
    id: "fu-003",
    emoji: "🥒",
    crop: "Dưa leo",
    farm: "Vườn dưa Nhơn Trạch",
    disease: "Phấn trắng (Powdery Mildew)",
    confidence: 61,
    reason: "low-confidence",
    reasonLabel: "AI chưa chắc chắn",
    deadline: "07/07/2026",
    hoursLeft: 48,
    severity: "medium",
    notes: "Confidence thấp, cần ảnh thêm góc độ khác",
    date: "01/07/2026",
  },
  {
    id: "fu-004",
    emoji: "🍅",
    crop: "Cà chua",
    farm: "Ruộng cà Long Thành",
    disease: "Héo rũ Fusarium",
    confidence: 55,
    reason: "expert",
    reasonLabel: "Cần chuyên gia xác nhận",
    deadline: "Chờ phản hồi",
    hoursLeft: null,
    severity: "high",
    notes: "Gửi cho chuyên gia Nguyễn Thị B — đang chờ xác nhận",
    date: "25/06/2026",
  },
];

const reasonConfig: Record<string, { color: string; icon: string }> = {
  camera: { color: "primary", icon: "ri-camera-line" },
  spreading: { color: "danger", icon: "ri-error-warning-line" },
  "low-confidence": { color: "warning", icon: "ri-question-line" },
  expert: { color: "info", icon: "ri-stethoscope-line" },
};

const severityBg: Record<string, string> = {
  critical: "rgba(239,68,68,0.06)",
  high: "rgba(255,193,7,0.06)",
  medium: "rgba(59,130,246,0.06)",
};

const severityBorder: Record<string, string> = {
  critical: "rgba(239,68,68,0.25)",
  high: "rgba(255,193,7,0.25)",
  medium: "rgba(59,130,246,0.2)",
};

export default function DiagnosisFollowUp() {
  const [dismissed, setDismissed] = useState<string[]>([]);

  const active = followUpCases.filter((c) => !dismissed.includes(c.id));

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-heart-pulse-line text-danger me-2"></i>
                  Ca cần theo dõi
                </h4>
                <p className="text-muted mb-0 fs-13">
                  {active.length} ca đang cần hành động ·{" "}
                  {followUpCases.filter((c) => c.severity === "critical").length} ca nghiêm trọng
                </p>
              </div>
              <Link href="/diagnosis/new">
                <Button color="success" id="btn-new-diag" size="sm" className="d-flex align-items-center gap-2">
                  <i className="ri-microscope-line"></i>Chẩn đoán mới
                </Button>
              </Link>
            </div>
          </Col>
        </Row>

        {/* Summary Row */}
        <Row className="mb-3">
          {[
            { label: "Chụp lại ảnh", count: active.filter(c => c.reason === "camera").length, color: "primary", icon: "ri-camera-line" },
            { label: "Đang lan rộng", count: active.filter(c => c.reason === "spreading").length, color: "danger", icon: "ri-error-warning-line" },
            { label: "AI chưa chắc", count: active.filter(c => c.reason === "low-confidence").length, color: "warning", icon: "ri-question-line" },
            { label: "Chờ chuyên gia", count: active.filter(c => c.reason === "expert").length, color: "info", icon: "ri-stethoscope-line" },
          ].map((s) => (
            <Col md={3} key={s.label} className="mb-2">
              <div className="d-flex align-items-center gap-3 p-3 rounded" style={{ border: "1px solid var(--vz-border-color)", background: "var(--vz-card-bg)" }}>
                <div className={`avatar-xs rounded bg-${s.color}-subtle d-flex align-items-center justify-content-center`} style={{ width: 36, height: 36 }}>
                  <i className={`${s.icon} text-${s.color} fs-16`}></i>
                </div>
                <div>
                  <h5 className="mb-0 fw-bold">{s.count}</h5>
                  <p className="mb-0 text-muted fs-12">{s.label}</p>
                </div>
              </div>
            </Col>
          ))}
        </Row>

        {/* Case Cards */}
        <Row>
          {active.length === 0 ? (
            <Col>
              <Card>
                <CardBody className="text-center py-5">
                  <i className="ri-checkbox-circle-line text-success fs-48 d-block mb-3"></i>
                  <h5 className="fw-semibold">Tất cả ca đã được xử lý!</h5>
                  <p className="text-muted">Không còn ca nào cần theo dõi.</p>
                  <Link href="/diagnosis/new">
                    <Button color="success" id="btn-all-done-new">Chẩn đoán mới</Button>
                  </Link>
                </CardBody>
              </Card>
            </Col>
          ) : (
            active.map((c) => {
              const rc = reasonConfig[c.reason];
              return (
                <Col xl={6} key={c.id} className="mb-3">
                  <Card
                    className="h-100"
                    id={c.id}
                    style={{
                      background: severityBg[c.severity],
                      border: `1px solid ${severityBorder[c.severity]}`,
                    }}
                  >
                    <CardBody className="p-4">
                      <div className="d-flex align-items-start justify-content-between mb-3">
                        <div className="d-flex align-items-center gap-2">
                          <span className="fs-24">{c.emoji}</span>
                          <div>
                            <h6 className="fw-bold mb-0">{c.disease}</h6>
                            <span className="text-muted fs-12">{c.crop} · {c.farm}</span>
                          </div>
                        </div>
                        <Badge color={rc.color} className="d-flex align-items-center gap-1">
                          <i className={rc.icon}></i>
                          {c.reasonLabel}
                        </Badge>
                      </div>

                      <div className="mb-3">
                        <div className="d-flex justify-content-between mb-1">
                          <span className="fs-12 text-muted">Độ tin cậy AI</span>
                          <span className={`fs-12 fw-bold text-${c.confidence >= 80 ? "success" : c.confidence >= 60 ? "warning" : "danger"}`}>
                            {c.confidence}%
                          </span>
                        </div>
                        <Progress
                          value={c.confidence}
                          color={c.confidence >= 80 ? "success" : c.confidence >= 60 ? "warning" : "danger"}
                          style={{ height: 6 }}
                        />
                      </div>

                      <div className="p-2 rounded mb-3" style={{ background: "rgba(0,0,0,0.04)" }}>
                        <p className="mb-0 fs-12 text-muted">
                          <i className="ri-information-line me-1"></i>
                          {c.notes}
                        </p>
                      </div>

                      <div className="d-flex align-items-center justify-content-between">
                        <div>
                          <span className="fs-12 text-muted">
                            <i className="ri-time-line me-1"></i>
                            {c.hoursLeft !== null ? (
                              c.hoursLeft < 0 ? (
                                <span className="text-danger fw-semibold">Quá hạn {Math.abs(c.hoursLeft)}h</span>
                              ) : (
                                `Còn ${c.hoursLeft}h — ${c.deadline}`
                              )
                            ) : (
                              c.deadline
                            )}
                          </span>
                        </div>
                        <div className="d-flex gap-2">
                          {c.reason === "camera" && (
                            <Link href="/diagnosis/new">
                              <Button size="sm" color="primary" id={`btn-recapture-${c.id}`}>
                                <i className="ri-camera-line me-1"></i>Chụp lại
                              </Button>
                            </Link>
                          )}
                          {c.reason === "expert" && (
                            <Link href="/expert/review">
                              <Button size="sm" color="info" id={`btn-expert-${c.id}`}>
                                <i className="ri-stethoscope-line me-1"></i>Xem trạng thái
                              </Button>
                            </Link>
                          )}
                          <Button
                            size="sm"
                            color="light"
                            id={`btn-dismiss-${c.id}`}
                            onClick={() => setDismissed([...dismissed, c.id])}
                          >
                            <i className="ri-check-line me-1"></i>Đã xử lý
                          </Button>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              );
            })
          )}
        </Row>
      </div>
    </div>
  );
}
