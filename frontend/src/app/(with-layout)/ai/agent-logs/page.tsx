"use client";

import React, { useState } from "react";
import { Badge, Button, Card, CardBody, Col, Progress, Row } from "reactstrap";
import Link from "next/link";

const traces = [
  {
    id: "trace-2026-0704-001",
    caseId: "CASE-2026-0704-001",
    crop: "Ớt",
    farm: "Vườn ớt Trảng Bom",
    disease: "Thán thư",
    confidence: 89,
    status: "saved",
    duration: "3.8s",
    createdAt: "04/07/2026 08:12",
  },
  {
    id: "trace-2026-0703-014",
    caseId: "CASE-2026-0703-014",
    crop: "Dưa leo",
    farm: "Vườn dưa Nhơn Trạch",
    disease: "Phấn trắng",
    confidence: 61,
    status: "expert",
    duration: "4.4s",
    createdAt: "03/07/2026 16:30",
  },
  {
    id: "trace-2026-0702-009",
    caseId: "CASE-2026-0702-009",
    crop: "Cà chua",
    farm: "Ruộng cà Long Thành",
    disease: "Đốm lá vi khuẩn",
    confidence: 92,
    status: "resolved",
    duration: "3.1s",
    createdAt: "02/07/2026 09:05",
  },
];

const agentSteps = [
  {
    agent: "Vision Agent",
    icon: "ri-eye-line",
    color: "primary",
    latency: "820 ms",
    input: "Ảnh lá/quả 1024x768",
    output:
      "Phát hiện đốm nâu lõm ở tâm, viền vàng nhạt. Xác suất thán thư ban đầu 74%.",
    evidence: ["lesion_count=14", "leaf_area_affected=18%", "image_quality=0.91"],
  },
  {
    agent: "Symptom Agent",
    icon: "ri-question-answer-line",
    color: "info",
    latency: "510 ms",
    input: "Câu hỏi triệu chứng cho nông dân",
    output:
      "Hỏi thêm thời điểm xuất hiện, có mưa kéo dài không, vết bệnh đã lan sang quả chưa.",
    evidence: ["rain_after=3 days", "fruit_spots=true", "spread_speed=medium"],
  },
  {
    agent: "Context Agent",
    icon: "ri-cloud-line",
    color: "cyan",
    latency: "430 ms",
    input: "Vườn, thời tiết, nhật ký chăm sóc",
    output:
      "Trảng Bom có mưa liên tục, độ ẩm 85-92%, chưa ghi nhận phun thuốc trong 7 ngày.",
    evidence: ["humidity=89%", "rainfall=42mm", "spray_gap=7d"],
  },
  {
    agent: "Reasoning Agent",
    icon: "ri-brain-line",
    color: "success",
    latency: "940 ms",
    input: "Vision + triệu chứng + bối cảnh",
    output:
      "Tăng xác suất thán thư từ 74% lên 89%; loại trừ cháy nắng và đốm lá vi khuẩn.",
    evidence: ["anthracnose=0.89", "bacterial_spot=0.08", "sunburn=0.03"],
  },
  {
    agent: "Safety Agent",
    icon: "ri-shield-check-line",
    color: "warning",
    latency: "390 ms",
    input: "Kết luận chẩn đoán và mức độ lan rộng",
    output:
      "Không khuyến nghị phun thuốc ngay. Ưu tiên IPM: tỉa lá bệnh, giảm ẩm, theo dõi 48h.",
    evidence: ["ipm_first=true", "chemical_advice=deferred", "expert_needed=false"],
  },
  {
    agent: "Diary Agent",
    icon: "ri-book-2-line",
    color: "secondary",
    latency: "260 ms",
    input: "Kết quả cuối cùng",
    output:
      "Lưu ca bệnh vào nhật ký mùa vụ, tạo lịch nhắc chụp lại ảnh sau 48h.",
    evidence: ["case_saved=true", "reminder=48h", "farm_log=created"],
  },
];

const statusConfig: Record<string, { color: string; label: string }> = {
  saved: { color: "success", label: "Đã lưu" },
  expert: { color: "warning", label: "Chờ chuyên gia" },
  resolved: { color: "info", label: "Đã xử lý" },
};

export default function AgentLogs() {
  const [selectedTrace, setSelectedTrace] = useState(traces[0]);

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
              <div>
                <div className="d-flex align-items-center gap-2 mb-1">
                  <Badge color="primary-subtle" className="text-primary">
                    AI-native workflow
                  </Badge>
                  <Badge color="light" className="text-muted">
                    Multi-agent trace
                  </Badge>
                </div>
                <h4 className="fw-semibold mb-1">Nhật ký Agent</h4>
                <p className="text-muted fs-13 mb-0">
                  Trace từng bước chẩn đoán: vision, triệu chứng, bối cảnh, suy luận, an toàn và nhật ký.
                </p>
              </div>
              <Link href="/diagnosis/new">
                <Button color="success" className="d-flex align-items-center gap-2">
                  <i className="ri-microscope-line"></i>
                  Chạy chẩn đoán mới
                </Button>
              </Link>
            </div>
          </Col>
        </Row>

        <Row>
          <Col xl={4} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Trace gần đây</h5>
                <div className="d-flex flex-column gap-2">
                  {traces.map((trace) => {
                    const active = selectedTrace.id === trace.id;
                    return (
                      <button
                        key={trace.id}
                        type="button"
                        onClick={() => setSelectedTrace(trace)}
                        className="text-start rounded p-3"
                        style={{
                          border: active
                            ? "1px solid rgba(45,206,137,0.7)"
                            : "1px solid var(--vz-border-color)",
                          background: active ? "rgba(45,206,137,0.08)" : "transparent",
                        }}
                      >
                        <div className="d-flex justify-content-between gap-2 mb-1">
                          <span className="fw-semibold fs-13">{trace.caseId}</span>
                          <Badge color={statusConfig[trace.status].color}>
                            {statusConfig[trace.status].label}
                          </Badge>
                        </div>
                        <p className="text-muted fs-12 mb-2">
                          {trace.crop} · {trace.farm}
                        </p>
                        <div className="d-flex justify-content-between text-muted fs-12">
                          <span>{trace.disease} · {trace.confidence}%</span>
                          <span>{trace.duration}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </Col>

          <Col xl={8} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
                  <div>
                    <h5 className="fw-semibold mb-1">{selectedTrace.caseId}</h5>
                    <p className="text-muted fs-13 mb-0">
                      {selectedTrace.crop} · {selectedTrace.farm} · {selectedTrace.createdAt}
                    </p>
                  </div>
                  <div className="text-end">
                    <Badge color={statusConfig[selectedTrace.status].color} className="mb-1">
                      {statusConfig[selectedTrace.status].label}
                    </Badge>
                    <p className="text-muted fs-12 mb-0">Tổng thời gian {selectedTrace.duration}</p>
                  </div>
                </div>

                <Row className="mb-3">
                  <Col md={4} className="mb-2">
                    <div className="p-3 rounded border h-100">
                      <p className="text-muted fs-12 mb-1">Bệnh kết luận</p>
                      <h6 className="fw-semibold mb-0">{selectedTrace.disease}</h6>
                    </div>
                  </Col>
                  <Col md={4} className="mb-2">
                    <div className="p-3 rounded border h-100">
                      <p className="text-muted fs-12 mb-1">Độ tin cậy</p>
                      <div className="d-flex align-items-center gap-2">
                        <Progress
                          value={selectedTrace.confidence}
                          color={selectedTrace.confidence >= 80 ? "success" : "warning"}
                          style={{ height: 7, flex: 1 }}
                        />
                        <span className="fw-semibold">{selectedTrace.confidence}%</span>
                      </div>
                    </div>
                  </Col>
                  <Col md={4} className="mb-2">
                    <div className="p-3 rounded border h-100">
                      <p className="text-muted fs-12 mb-1">Agent đã chạy</p>
                      <h6 className="fw-semibold mb-0">{agentSteps.length} bước</h6>
                    </div>
                  </Col>
                </Row>

                <div className="position-relative">
                  <div
                    className="position-absolute top-0 bottom-0"
                    style={{
                      left: 18,
                      width: 2,
                      background: "var(--vz-border-color)",
                    }}
                  />
                  <div className="d-flex flex-column gap-3">
                    {agentSteps.map((step, index) => (
                      <div key={step.agent} className="d-flex gap-3 position-relative">
                        <div
                          className={`bg-${step.color}-subtle text-${step.color} rounded-circle d-flex align-items-center justify-content-center flex-shrink-0`}
                          style={{
                            width: 38,
                            height: 38,
                            border: "3px solid var(--vz-card-bg)",
                            zIndex: 1,
                          }}
                        >
                          <i className={step.icon}></i>
                        </div>
                        <div className="border rounded p-3 flex-grow-1">
                          <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2">
                            <div>
                              <p className="fw-semibold mb-0">
                                {index + 1}. {step.agent}
                              </p>
                              <p className="text-muted fs-12 mb-0">Input: {step.input}</p>
                            </div>
                            <Badge color="light" className="text-muted">
                              {step.latency}
                            </Badge>
                          </div>
                          <p className="fs-13 mb-3">{step.output}</p>
                          <div className="d-flex flex-wrap gap-2">
                            {step.evidence.map((item) => (
                              <code key={item} className="fs-12 px-2 py-1 rounded bg-light">
                                {item}
                              </code>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
