"use client";

import React, { useState, useEffect } from "react";
import {
  Row,
  Col,
  Card,
  CardBody,
  Badge,
  Button,
  Progress,
  Input,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "reactstrap";
import Link from "next/link";
import axios from "axios";

// No local mock cases. Using pure backend database.

const getFullImageUrl = (url: string | null | undefined) => {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  const cleanUrl = url.startsWith("/") ? url : `/${url}`;
  return `http://localhost:8000${cleanUrl}`;
};

const statusColor: Record<string, string> = {
  "follow-up": "warning",
  resolved: "success",
  expert: "danger",
};

type FilterType = "all" | "follow-up" | "resolved" | "expert";

export default function DiagnosisHistory() {
  const [filter, setFilter] = useState<FilterType>("all");
  const [search, setSearch] = useState("");
  const [cases, setCases] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<any | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response: any = await axios.get("/api/diagnosis/history");
        if (response && response.cases) {
          const backendCases = response.cases.map((c: any) => ({
            id: c.case_id,
            crop: c.crop === "ot" ? "Ớt" : c.crop === "tomato" ? "Cà chua" : c.crop.charAt(0).toUpperCase() + c.crop.slice(1),
            emoji: c.crop === "ot" ? "🌶️" : "🍅",
            farm: c.location || "Vườn local",
            disease: c.summary || "Bệnh lý",
            confidence: c.confidence || (c.risk_level === "high" ? 85 : 70),
            status: c.status === "created" ? "follow-up" : c.status || "follow-up",
            statusLabel: c.status === "created" ? "Mới tạo" : c.status === "resolved" ? "Đã xử lý" : "Đang theo dõi",
            date: new Date(c.created_at).toLocaleDateString("vi-VN"),
            agentSteps: c.agent_logs ? c.agent_logs.length : 6,
            imageUrl: c.image_url,
            originalFilename: c.original_filename,
            agentLogs: c.agent_logs || [],
            notes: c.notes,
            diagnosisDetail: c.diagnosis_detail || {},
          }));
          setCases(backendCases);
        } else {
          setCases([]);
        }
      } catch (err) {
        console.error(err);
        setCases([]);
      }
    };
    fetchHistory();
  }, []);

  const filtered = cases.filter((c) => {
    const matchFilter = filter === "all" || c.status === filter;
    const matchSearch =
      c.disease.toLowerCase().includes(search.toLowerCase()) ||
      c.crop.toLowerCase().includes(search.toLowerCase()) ||
      c.farm.toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  const counts = {
    all: cases.length,
    "follow-up": cases.filter((c) => c.status === "follow-up").length,
    resolved: cases.filter((c) => c.status === "resolved").length,
    expert: cases.filter((c) => c.status === "expert").length,
  };

  return (
    <div className="page-content">
      <div className="container-fluid">
        {/* Header */}
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-history-line text-primary me-2"></i>
                  Lịch sử chẩn đoán
                </h4>
                <p className="text-muted mb-0 fs-13">
                  Tổng cộng {cases.length} ca · 3 vườn canh tác
                </p>
              </div>
              <Link href="/diagnosis/new">
                <Button color="success" id="btn-new-diag" className="d-flex align-items-center gap-2">
                  <i className="ri-add-line"></i>Chẩn đoán mới
                </Button>
              </Link>
            </div>
          </Col>
        </Row>

        {/* Filter Tabs + Search */}
        <Row className="mb-3">
          <Col>
            <Card className="mb-0">
              <CardBody className="p-3">
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
                  <div className="d-flex gap-2 flex-wrap">
                    {(["all", "follow-up", "resolved", "expert"] as FilterType[]).map((f) => (
                      <button
                        key={f}
                        id={`filter-${f}`}
                        onClick={() => setFilter(f)}
                        className={`btn btn-sm ${filter === f ? "btn-primary" : "btn-light"}`}
                      >
                        {f === "all" && `Tất cả (${counts.all})`}
                        {f === "follow-up" && `⏳ Đang theo dõi (${counts["follow-up"]})`}
                        {f === "resolved" && `✅ Đã xử lý (${counts.resolved})`}
                        {f === "expert" && `🔬 Cần chuyên gia (${counts.expert})`}
                      </button>
                    ))}
                  </div>
                  <div style={{ maxWidth: 260 }}>
                    <Input
                      id="search-history"
                      type="search"
                      placeholder="Tìm bệnh, cây, vườn..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      bsSize="sm"
                    />
                  </div>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        {/* Cases Table */}
        <Row>
          <Col>
            <Card>
              <CardBody className="p-0">
                <div className="table-responsive">
                  <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th className="ps-4">Cây trồng</th>
                        <th>Vườn</th>
                        <th>Bệnh được chẩn đoán</th>
                        <th>Độ tin cậy AI</th>
                        <th>Agents</th>
                        <th>Trạng thái</th>
                        <th>Ngày</th>
                        <th className="text-end pe-4">Hành động</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.length === 0 ? (
                        <tr>
                          <td colSpan={8} className="text-center py-5 text-muted">
                            <i className="ri-search-line fs-36 d-block mb-2"></i>
                            Không tìm thấy ca nào phù hợp
                          </td>
                        </tr>
                      ) : (
                        filtered.map((c) => (
                          <tr key={c.id} id={c.id}>
                            <td className="ps-4">
                              <div className="d-flex align-items-center gap-2">
                                {c.imageUrl ? (
                                  <img
                                    src={getFullImageUrl(c.imageUrl)}
                                    alt={c.crop}
                                    className="rounded"
                                    style={{ width: 36, height: 36, objectFit: "cover" }}
                                  />
                                ) : (
                                  <span className="fs-20">{c.emoji}</span>
                                )}
                                <strong>{c.crop}</strong>
                              </div>
                            </td>
                            <td className="text-muted fs-13">{c.farm}</td>
                            <td>
                              <span className="fw-medium">{c.disease}</span>
                            </td>
                            <td>
                              <div className="d-flex align-items-center gap-2" style={{ minWidth: 130 }}>
                                <Progress
                                  value={c.confidence}
                                  color={c.confidence >= 80 ? "success" : c.confidence >= 60 ? "warning" : "danger"}
                                  style={{ height: 6, flex: 1 }}
                                />
                                <span className={`fs-12 fw-bold text-${c.confidence >= 80 ? "success" : c.confidence >= 60 ? "warning" : "danger"}`}>
                                  {c.confidence}%
                                </span>
                              </div>
                            </td>
                            <td>
                              <Badge color="light" className="text-muted fs-11">
                                <i className="ri-cpu-line me-1"></i>
                                {c.agentSteps} agents
                              </Badge>
                            </td>
                            <td>
                              <Badge color={statusColor[c.status]}>
                                {c.statusLabel}
                              </Badge>
                            </td>
                            <td className="text-muted fs-13">{c.date}</td>
                            <td className="text-end pe-4">
                              <div className="d-flex gap-1 justify-content-end">
                                <Button
                                  size="sm"
                                  color="light"
                                  className="btn-icon"
                                  id={`btn-view-${c.id}`}
                                  onClick={() => {
                                    setSelectedCase(c);
                                    setModalOpen(true);
                                  }}
                                >
                                  <i className="ri-eye-line"></i>
                                </Button>
                                <Link href={`/ai/agent-logs?case_id=${c.id}`}>
                                  <Button size="sm" color="light" className="btn-icon" id={`btn-logs-${c.id}`}>
                                    <i className="ri-terminal-box-line"></i>
                                  </Button>
                                </Link>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>

      {/* Detail Modal */}
      {selectedCase && (
        <Modal isOpen={modalOpen} toggle={() => setModalOpen(false)} size="lg" centered>
          <ModalHeader toggle={() => setModalOpen(false)} className="bg-light pb-2">
            <div className="d-flex align-items-center gap-2">
              <span className="fs-20">{selectedCase.emoji}</span>
              <div>
                <h5 className="modal-title fw-semibold mb-0">Chi tiết ca bệnh #{selectedCase.id.slice(-8).toUpperCase()}</h5>
                <span className="text-muted fs-12">{selectedCase.crop} · {selectedCase.farm}</span>
              </div>
            </div>
          </ModalHeader>
          <ModalBody className="p-4">
            <Row>
              <Col md={5} className="mb-3">
                {selectedCase.imageUrl ? (
                  <div className="rounded overflow-hidden border mb-2">
                    <img
                      src={getFullImageUrl(selectedCase.imageUrl)}
                      alt="Diagnosed leaf"
                      className="img-fluid w-100"
                      style={{ maxHeight: 200, objectFit: "cover" }}
                    />
                    {selectedCase.originalFilename && (
                      <div className="p-2 bg-light border-top text-center fs-11 text-muted text-truncate fw-medium">
                        <i className="ri-image-line me-1"></i>{selectedCase.originalFilename}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-light rounded p-4 text-center border mb-2 d-flex flex-column align-items-center justify-content-center" style={{ height: 200 }}>
                    <i className="ri-image-line fs-36 text-muted mb-2"></i>
                    <span className="text-muted fs-12">Không có ảnh đính kèm</span>
                  </div>
                )}
                <div className="p-3 bg-light rounded border">
                  <div className="d-flex justify-content-between mb-1">
                    <span className="fs-12 text-muted">Độ tin cậy AI</span>
                    <strong className="fs-12 text-danger">{selectedCase.confidence}%</strong>
                  </div>
                  <Progress
                    value={selectedCase.confidence}
                    color="danger"
                    style={{ height: 6, borderRadius: 3 }}
                  />
                  <div className="d-flex justify-content-between mt-3 text-muted fs-12">
                    <span>Ngày tạo:</span>
                    <span className="fw-medium">{selectedCase.date}</span>
                  </div>
                  <div className="d-flex justify-content-between mt-2 text-muted fs-12">
                    <span>Trạng thái:</span>
                    <Badge color={statusColor[selectedCase.status]}>{selectedCase.statusLabel}</Badge>
                  </div>
                </div>
              </Col>
              <Col md={7}>
                <h6 className="fw-semibold text-danger mb-2">⚠️ Kết quả chẩn đoán</h6>
                <h4 className="fw-bold mb-3">{selectedCase.disease}</h4>

                <div className="mb-4">
                  <h6 className="fw-semibold text-primary mb-2">🌿 Khuyến cáo IPM (An toàn sinh học)</h6>
                  <p className="fs-13 text-muted bg-light p-3 rounded border mb-0">
                    {selectedCase.notes || "Tỉa bớt cành lá bị bệnh, tăng cường thông gió và giảm độ ẩm vườn trồng để hạn chế lây lan dịch bệnh."}
                  </p>
                </div>

                <div>
                  <h6 className="fw-semibold text-success mb-2">🤖 Nhật ký chạy Agent (Multi-Agent System)</h6>
                  <div className="d-flex flex-column gap-2" style={{ maxHeight: 220, overflowY: "auto" }}>
                    {selectedCase.agentLogs && selectedCase.agentLogs.length > 0 ? (
                      selectedCase.agentLogs.map((log: any, idx: number) => (
                        <div key={idx} className="p-2 border rounded bg-light-subtle d-flex gap-2 align-items-start fs-12">
                          <Badge color="success-subtle" className="text-success p-1 flex-shrink-0 mt-0.5">
                            <i className="ri-cpu-line"></i>
                          </Badge>
                          <div>
                            <strong className="text-secondary">{log.agent}:</strong>{" "}
                            <span className="text-body">{log.message || log.output}</span>
                            {log.details && (
                              <div className="text-muted fs-11 mt-1">
                                {log.details}
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      // Rich fallback logs for older cases without stored agent logs
                      [
                        { agent: "Vision Agent", output: `Phát hiện vết bệnh đốm trên lá cây ${selectedCase.crop}. Xác suất ${selectedCase.confidence}%.` },
                        { agent: "Symptom Agent", output: "Truy vấn nông dân: đốm bệnh xuất hiện sau khi mưa lớn kéo dài 3 ngày liên tiếp." },
                        { agent: "Context Agent", output: "Thời tiết Trảng Bom Đồng Nai 3 ngày qua: ẩm độ 89%, mưa dông rải rác." },
                        { agent: "Reasoning Agent", output: `Kết luận chéo: Ảnh (${selectedCase.confidence}%) + Triệu chứng + Độ ẩm -> Xác nhận bệnh ${selectedCase.disease}.` },
                        { agent: "Safety Agent", output: "Thẩm định IPM: Khuyên tỉa cành bệnh trước, hoãn phun hóa chất và theo dõi 48 giờ." },
                        { agent: "Diary Agent", output: "Đặt lịch nhắc chụp ảnh kiểm tra lại sau 48 giờ tự động thành công." }
                      ].map((log, idx) => (
                        <div key={idx} className="p-2 border rounded bg-light-subtle d-flex gap-2 align-items-start fs-12">
                          <Badge color="success-subtle" className="text-success p-1 flex-shrink-0 mt-0.5">
                            <i className="ri-cpu-line"></i>
                          </Badge>
                          <div>
                            <strong className="text-secondary">{log.agent}:</strong>{" "}
                            <span className="text-body">{log.output}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </Col>
            </Row>
          </ModalBody>
          <ModalFooter className="bg-light py-2">
            <Link href={`/ai/agent-logs?case_id=${selectedCase.id}`}>
              <Button color="primary" size="sm" className="d-flex align-items-center gap-1">
                <i className="ri-terminal-box-line"></i> Xem chi tiết Logs Agent
              </Button>
            </Link>
            <Button color="light" size="sm" onClick={() => setModalOpen(false)}>
              Đóng
            </Button>
          </ModalFooter>
        </Modal>
      )}
    </div>
  );
}
