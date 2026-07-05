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
} from "reactstrap";
import Link from "next/link";
import axios from "axios";

const allCases = [
  {
    id: "hist-001",
    crop: "Ớt",
    emoji: "🌶️",
    farm: "Vườn ớt Trảng Bom",
    disease: "Thán thư (Anthracnose)",
    confidence: 89,
    status: "follow-up",
    statusLabel: "Đang theo dõi",
    date: "04/07/2026",
    agentSteps: 6,
  },
  {
    id: "hist-002",
    crop: "Cà chua",
    emoji: "🍅",
    farm: "Ruộng cà Long Thành",
    disease: "Đốm lá vi khuẩn",
    confidence: 92,
    status: "resolved",
    statusLabel: "Đã xử lý",
    date: "02/07/2026",
    agentSteps: 5,
  },
  {
    id: "hist-003",
    crop: "Dưa leo",
    emoji: "🥒",
    farm: "Vườn dưa Nhơn Trạch",
    disease: "Phấn trắng (Powdery Mildew)",
    confidence: 61,
    status: "expert",
    statusLabel: "Cần chuyên gia",
    date: "01/07/2026",
    agentSteps: 6,
  },
  {
    id: "hist-004",
    crop: "Ớt",
    emoji: "🌶️",
    farm: "Vườn ớt Trảng Bom",
    disease: "Héo xanh vi khuẩn",
    confidence: 78,
    status: "follow-up",
    statusLabel: "Đang theo dõi",
    date: "30/06/2026",
    agentSteps: 6,
  },
  {
    id: "hist-005",
    crop: "Cải xanh",
    emoji: "🥬",
    farm: "Vườn rau Cẩm Mỹ",
    disease: "Sâu tơ (Diamond-back moth)",
    confidence: 95,
    status: "resolved",
    statusLabel: "Đã xử lý",
    date: "29/06/2026",
    agentSteps: 5,
  },
  {
    id: "hist-006",
    crop: "Lúa",
    emoji: "🌾",
    farm: "Ruộng lúa Nhơn Trạch",
    disease: "Đạo ôn (Rice Blast)",
    confidence: 83,
    status: "resolved",
    statusLabel: "Đã xử lý",
    date: "27/06/2026",
    agentSteps: 6,
  },
  {
    id: "hist-007",
    crop: "Cà chua",
    emoji: "🍅",
    farm: "Ruộng cà Long Thành",
    disease: "Héo rũ Fusarium",
    confidence: 55,
    status: "expert",
    statusLabel: "Cần chuyên gia",
    date: "25/06/2026",
    agentSteps: 6,
  },
  {
    id: "hist-008",
    crop: "Ớt",
    emoji: "🌶️",
    farm: "Vườn ớt Trảng Bom",
    disease: "Thán thư (Anthracnose)",
    confidence: 91,
    status: "resolved",
    statusLabel: "Đã xử lý",
    date: "20/06/2026",
    agentSteps: 6,
  },
];

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

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get("/api/diagnosis/history");
        if (response.data && response.data.cases) {
          const backendCases = response.data.cases.map((c: any) => ({
            id: c.case_id,
            crop: c.crop === "ot" ? "Ớt" : c.crop === "tomato" ? "Cà chua" : c.crop.charAt(0).toUpperCase() + c.crop.slice(1),
            emoji: c.crop === "ot" ? "🌶️" : "🍅",
            farm: c.location || "Vườn local",
            disease: c.summary || "Bệnh lý",
            confidence: c.risk_level === "high" ? 85 : 70,
            status: c.status === "created" ? "follow-up" : c.status || "follow-up",
            statusLabel: c.status === "created" ? "Mới tạo" : c.status === "resolved" ? "Đã xử lý" : "Đang theo dõi",
            date: new Date(c.created_at).toLocaleDateString("vi-VN"),
            agentSteps: 5,
          }));
          setCases([...backendCases, ...allCases]);
        } else {
          setCases(allCases);
        }
      } catch (err) {
        console.error(err);
        setCases(allCases);
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
                              <span className="fs-20 me-2">{c.emoji}</span>
                              <strong>{c.crop}</strong>
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
                                <Button size="sm" color="light" className="btn-icon" id={`btn-view-${c.id}`}>
                                  <i className="ri-eye-line"></i>
                                </Button>
                                <Link href="/ai/agent-logs">
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
    </div>
  );
}
