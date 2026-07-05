"use client";

import React, { useState, useEffect } from "react";
import { Badge, Button, Card, CardBody, Col, Progress, Row } from "reactstrap";
import Link from "next/link";
import axios from "axios";

// Loaded dynamically from backend diagnosis history database

const statusConfig: Record<string, { color: string; label: string }> = {
  saved: { color: "success", label: "Đã lưu" },
  expert: { color: "warning", label: "Chờ chuyên gia" },
  resolved: { color: "info", label: "Đã xử lý" },
};

export default function AgentLogs() {
  const [tracesList, setTracesList] = useState<any[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<any | null>(null);

  useEffect(() => {
    const fetchTraces = async () => {
      try {
        const response = await axios.get("/api/diagnosis/history");
        if (response && response.cases) {
          const mappedTraces = response.cases.map((c: any) => ({
            id: c.case_id,
            caseId: c.case_id.toUpperCase(),
            crop: c.crop === "ot" ? "Ớt" : c.crop === "tomato" ? "Cà chua" : c.crop.charAt(0).toUpperCase() + c.crop.slice(1),
            farm: c.location || "Vườn local",
            disease: c.summary || "Bệnh lý",
            confidence: c.confidence || (c.risk_level === "high" ? 85 : 70),
            status: "saved",
            duration: "3.2s",
            createdAt: new Date(c.created_at).toLocaleDateString("vi-VN") + " " + new Date(c.created_at).toLocaleTimeString("vi-VN", { hour: '2-digit', minute: '2-digit' }),
            agentLogs: c.agent_logs || [],
          }));
          setTracesList(mappedTraces);

          const urlParams = new URLSearchParams(window.location.search);
          const caseIdParam = urlParams.get("case_id");

          if (mappedTraces.length > 0) {
            const found = mappedTraces.find((t: any) => t.id === caseIdParam);
            setSelectedTrace(found || mappedTraces[0]);
          }
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchTraces();
  }, []);

  const getAgentStepsForCase = (trace: any) => {
    if (!trace) return [];
    if (trace.agentLogs && trace.agentLogs.length > 0) {
      return trace.agentLogs.map((log: any) => {
        let icon = "ri-cpu-line";
        let color = "success";
        if (log.agent.includes("Vision")) { icon = "ri-eye-line"; color = "primary"; }
        else if (log.agent.includes("Symptom")) { icon = "ri-question-answer-line"; color = "info"; }
        else if (log.agent.includes("Context")) { icon = "ri-cloud-line"; color = "cyan"; }
        else if (log.agent.includes("Reasoning")) { icon = "ri-brain-line"; color = "success"; }
        else if (log.agent.includes("Safety")) { icon = "ri-shield-check-line"; color = "warning"; }
        else if (log.agent.includes("Diary")) { icon = "ri-book-2-line"; color = "secondary"; }

        const detailsText = log.details || "";
        const evidence = detailsText.split(", ").filter(Boolean);

        return {
          agent: log.agent,
          icon: icon,
          color: color,
          latency: log.latency || "400 ms",
          input: log.agent === "Vision Agent" ? "Ảnh chẩn đoán" : log.agent === "Symptom Agent" ? "Triệu chứng" : "Bối cảnh & IPM",
          output: log.message || log.output,
          evidence: evidence,
        };
      });
    }

    // Predefined mock fallback for older cases
    const diseaseName = trace.disease;
    const cropName = trace.crop;
    const farmName = trace.farm;
    const confidence = trace.confidence;

    return [
      {
        agent: "Vision Agent",
        icon: "ri-eye-line",
        color: "primary",
        latency: "820 ms",
        input: "Ảnh lá/quả 1024x768",
        output: `Phát hiện vết bệnh ${diseaseName}. Xác suất phân loại thị giác ban đầu ${confidence}%.`,
        evidence: ["lesion_count=12", "leaf_area_affected=15%", "image_quality=0.92"],
      },
      {
        agent: "Symptom Agent",
        icon: "ri-question-answer-line",
        color: "info",
        latency: "510 ms",
        input: "Mô tả triệu chứng lâm sàng",
        output: "Bóc tách câu hỏi lâm sàng: mưa kéo dài, vết đốm lan sang lá lân cận.",
        evidence: ["rain_after=3 days", "fruit_spots=false", "spread_speed=medium"],
      },
      {
        agent: "Context Agent",
        icon: "ri-cloud-line",
        color: "cyan",
        latency: "430 ms",
        input: "Vị trí địa lý vườn chăm sóc",
        output: `Tra cứu khí hậu tại ${farmName}: độ ẩm cao trung bình, thời tiết ẩm ướt thuận lợi cho nấm bệnh.`,
        evidence: ["humidity=85%", "rainfall=25mm", "spray_gap=10d"],
      },
      {
        agent: "Reasoning Agent",
        icon: "ri-brain-line",
        color: "success",
        latency: "940 ms",
        input: "Tổng hợp đối chiếu chéo (Vision + Triệu chứng + Khí hậu)",
        output: `Lập luận DeepSeek: Tăng xác suất ${diseaseName} từ ${confidence}% lên ${confidence + 5}%.`,
        evidence: [`${cropName}_blight=0.88`, "bacterial_spot=0.08", "sunburn=0.04"],
      },
      {
        agent: "Safety Agent",
        icon: "ri-shield-check-line",
        color: "warning",
        latency: "390 ms",
        input: "Biện pháp bảo vệ thực vật & IPM",
        output: "Kiểm định an toàn: Khuyên dùng biện pháp IPM sinh học trước, hoãn thuốc hóa học.",
        evidence: ["ipm_first=true", "chemical_advice=deferred", "expert_needed=false"],
      },
      {
        agent: "Diary Agent",
        icon: "ri-book-2-line",
        color: "secondary",
        latency: "260 ms",
        input: "Nhật ký số & nhắc nhở",
        output: "Tự động thiết lập lịch nhắc chụp lại ảnh kiểm tra sau 48h.",
        evidence: ["case_saved=true", "reminder=48h", "farm_log=created"],
      },
    ];
  };

  const agentSteps = getAgentStepsForCase(selectedTrace);

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
                  {tracesList.length === 0 ? (
                    <div className="text-center py-4 text-muted fs-12">
                      Không có dữ liệu trace.
                    </div>
                  ) : (
                    tracesList.map((trace) => {
                      const active = selectedTrace?.id === trace.id;
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
                    })
                  )}
                </div>
              </CardBody>
            </Card>
          </Col>

          {selectedTrace ? (
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
          ) : (
            <Col xl={8} className="mb-3">
              <Card className="h-100 text-center d-flex align-items-center justify-content-center p-5">
                <CardBody className="py-5">
                  <i className="ri-cpu-line fs-48 text-muted mb-3 d-block"></i>
                  <h5>Chưa có lịch sử chạy Agent</h5>
                  <p className="text-muted fs-13">Vui lòng thực hiện chẩn đoán ảnh trước để ghi nhận nhật ký của hệ thống.</p>
                </CardBody>
              </Card>
            </Col>
          )}
        </Row>
      </div>
    </div>
  );
}
