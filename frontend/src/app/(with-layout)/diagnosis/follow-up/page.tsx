"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button, Progress } from "reactstrap";
import Link from "next/link";
import axios from "axios";

// Pure backend data loaded dynamically.

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
  const [cases, setCases] = useState<any[]>([]);
  const [dismissed, setDismissed] = useState<string[]>([]);

  useEffect(() => {
    const fetchFollowUp = async () => {
      try {
        const response: any = await axios.get("/api/diagnosis/follow-up");
        if (response) {
          const list: any[] = [];
          
          if (response.cases_waiting_for_symptoms) {
            response.cases_waiting_for_symptoms.forEach((c: any) => {
              list.push({
                id: c.case_id,
                emoji: c.crop === "ot" ? "🌶️" : "🍅",
                crop: c.crop === "ot" ? "Ớt" : c.crop === "tomato" ? "Cà chua" : c.crop.charAt(0).toUpperCase() + c.crop.slice(1),
                farm: c.location || "Vườn local",
                disease: c.summary || "Cần cung cấp thêm triệu chứng",
                confidence: 60,
                reason: "low-confidence",
                reasonLabel: "Chờ thông tin lâm sàng",
                deadline: "Hỏi thêm triệu chứng",
                hoursLeft: 24,
                severity: "medium",
                notes: c.notes || "Hệ thống AI Agent cần thêm câu trả lời từ nông dân để kết luận chính xác.",
                date: new Date(c.created_at || new Date()).toLocaleDateString("vi-VN"),
              });
            });
          }

          if (response.pending_expert_reviews) {
            response.pending_expert_reviews.forEach((r: any) => {
              list.push({
                id: r.review_id || r.case_id,
                emoji: "🔬",
                crop: "Cây trồng",
                farm: r.location || "Hợp tác xã",
                disease: r.notes || "Chờ ý kiến chuyên gia",
                confidence: 85,
                reason: "expert",
                reasonLabel: "Chờ chuyên gia duyệt",
                deadline: "Đang chờ duyệt",
                hoursLeft: null,
                severity: "high",
                notes: r.comments || "Đã gửi mẫu bệnh về trạm bảo vệ thực vật để kiểm định.",
                date: new Date(r.created_at || new Date()).toLocaleDateString("vi-VN"),
              });
            });
          }

          if (response.active_reminders) {
            response.active_reminders.forEach((rem: any) => {
              const due = rem.due_at ? new Date(rem.due_at) : new Date();
              const hours = Math.round((due.getTime() - new Date().getTime()) / 3600000);
              list.push({
                id: rem.reminder_id,
                emoji: "⏰",
                crop: "Nông trại",
                farm: "Khu vực theo dõi",
                disease: rem.message || "Lịch nhắc chụp lại ảnh kiểm tra",
                confidence: 90,
                reason: "camera",
                reasonLabel: "Theo dõi 48h",
                deadline: due.toLocaleString("vi-VN"),
                hoursLeft: hours,
                severity: rem.priority === "high" ? "critical" : "high",
                notes: rem.message || "Chụp ảnh lá sau 48h để đánh giá tốc độ phát triển của bệnh.",
                date: new Date(rem.created_at || new Date()).toLocaleDateString("vi-VN"),
              });
            });
          }

          setCases(list);
        }
      } catch (err) {
        console.error("Fetch follow-up error", err);
      }
    };
    fetchFollowUp();
  }, []);

  const active = cases.filter((c) => !dismissed.includes(c.id));

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
                  {cases.filter((c) => c.severity === "critical").length} ca nghiêm trọng
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
