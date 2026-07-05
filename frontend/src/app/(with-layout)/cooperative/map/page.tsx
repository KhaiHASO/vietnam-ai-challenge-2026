"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button } from "reactstrap";
import ReactApexChart from "react-apexcharts";
import axios from "axios";

// Mock disease outbreak locations (simulated as district data)
const mapDistricts = [
  { id: "trang-bom", name: "Trảng Bom", lat: 10.96, lng: 107.01, cases: 12, trend: "up", severity: "high", crops: ["Ớt", "Cà chua"] },
  { id: "long-thanh", name: "Long Thành", lat: 10.79, lng: 107.04, cases: 7, trend: "stable", severity: "medium", crops: ["Cà chua", "Lúa"] },
  { id: "nhon-trach", name: "Nhơn Trạch", lat: 10.72, lng: 106.99, cases: 5, trend: "down", severity: "low", crops: ["Dưa leo"] },
  { id: "cam-my", name: "Cẩm Mỹ", lat: 10.92, lng: 107.16, cases: 3, trend: "stable", severity: "low", crops: ["Rau cải"] },
  { id: "xuan-loc", name: "Xuân Lộc", lat: 10.93, lng: 107.42, cases: 8, trend: "up", severity: "medium", crops: ["Lúa", "Tiêu"] },
];

const recentAlerts = [
  {
    id: "alert-1",
    district: "Trảng Bom",
    disease: "Thán thư trên ớt",
    cases: 12,
    trend: "up",
    date: "04/07/2026",
    severity: "high",
  },
  {
    id: "alert-2",
    district: "Xuân Lộc",
    disease: "Đạo ôn trên lúa",
    cases: 8,
    trend: "up",
    date: "03/07/2026",
    severity: "medium",
  },
  {
    id: "alert-3",
    district: "Long Thành",
    disease: "Đốm lá vi khuẩn",
    cases: 7,
    trend: "stable",
    date: "02/07/2026",
    severity: "medium",
  },
  {
    id: "alert-4",
    district: "Nhơn Trạch",
    disease: "Phấn trắng dưa leo",
    cases: 5,
    trend: "down",
    date: "01/07/2026",
    severity: "low",
  },
];

const weeklyTrendSeries = [
  {
    name: "Trảng Bom",
    data: [5, 7, 8, 9, 10, 11, 12],
  },
  {
    name: "Xuân Lộc",
    data: [3, 4, 5, 6, 6, 7, 8],
  },
  {
    name: "Long Thành",
    data: [6, 7, 7, 6, 7, 7, 7],
  },
];

const weeklyChartOptions: any = {
  chart: { type: "line", height: 200, toolbar: { show: false }, fontFamily: "Inter, sans-serif" },
  colors: ["#ef4444", "#f59e0b", "#3b82f6"],
  stroke: { curve: "smooth", width: 2 },
  xaxis: { categories: ["28/6", "29/6", "30/6", "1/7", "2/7", "3/7", "4/7"], labels: { style: { fontSize: "11px" } } },
  yaxis: { labels: { style: { fontSize: "11px" } }, title: { text: "Số ca", style: { fontSize: "11px" } } },
  legend: { position: "top" },
  grid: { strokeDashArray: 3 },
  tooltip: { shared: true },
};

const heatmapSeries = [
  { name: "Ớt", data: [12, 3, 0, 0, 0] },
  { name: "Cà chua", data: [5, 7, 0, 0, 0] },
  { name: "Lúa", data: [0, 4, 0, 0, 8] },
  { name: "Dưa leo", data: [0, 0, 5, 0, 0] },
  { name: "Rau cải", data: [0, 0, 0, 3, 0] },
];

const heatmapOptions: any = {
  chart: { type: "heatmap", height: 200, toolbar: { show: false }, fontFamily: "Inter, sans-serif" },
  colors: ["#ef4444"],
  xaxis: { categories: ["Trảng Bom", "Long Thành", "Nhơn Trạch", "Cẩm Mỹ", "Xuân Lộc"], labels: { style: { fontSize: "10px" } } },
  dataLabels: { enabled: true, style: { fontSize: "11px" } },
  title: { text: "Ca bệnh theo cây trồng × khu vực", style: { fontSize: "12px" } },
};

const severityConfig: Record<string, { color: string; label: string; dot: string }> = {
  high: { color: "danger", label: "Cao", dot: "#ef4444" },
  medium: { color: "warning", label: "Trung bình", dot: "#f59e0b" },
  low: { color: "success", label: "Thấp", dot: "#2dce89" },
};

export default function CooperativeMap() {
  const [districts, setDistricts] = useState<any[]>(mapDistricts);
  const [selectedDistrict, setSelectedDistrict] = useState<any | null>(null);

  useEffect(() => {
    const fetchCooperativeMap = async () => {
      try {
        const response = await axios.get("/api/listing/cooperative-disease-map");
        if (response.data && response.data.map_points && response.data.map_points.length > 0) {
          const points = response.data.map_points;
          const updatedDistricts = mapDistricts.map((d) => {
            const matchCount = points.filter((p: any) => 
              (p.location && p.location.toLowerCase().includes(d.name.toLowerCase())) || 
              (p.farm_name && p.farm_name.toLowerCase().includes(d.name.toLowerCase()))
            ).length;
            
            const totalCasesCount = d.cases + matchCount;
            return {
              ...d,
              cases: totalCasesCount,
              severity: totalCasesCount > 10 ? "high" : totalCasesCount > 5 ? "medium" : "low",
            };
          });
          setDistricts(updatedDistricts);
        } else {
          setDistricts(mapDistricts);
        }
      } catch (err) {
        console.error(err);
        setDistricts(mapDistricts);
      }
    };
    fetchCooperativeMap();
  }, []);

  const totalCases = districts.reduce((s, d) => s + d.cases, 0);
  const highRisk = districts.filter((d) => d.severity === "high").length;

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-map-pin-2-line text-danger me-2"></i>
                  Bản đồ ca bệnh
                </h4>
                <p className="text-muted mb-0 fs-13">
                  Đồng Nai · Tuần 27/2026 · {totalCases} ca đang theo dõi toàn tỉnh
                </p>
              </div>
              <div className="d-flex gap-2">
                <Badge color="danger" className="d-flex align-items-center gap-1 px-3 py-2">
                  <i className="ri-error-warning-line"></i> {highRisk} vùng nguy hiểm
                </Badge>
              </div>
            </div>
          </Col>
        </Row>

        {/* KPI Row */}
        <Row className="mb-3">
          {[
            { label: "Tổng ca toàn tỉnh", value: totalCases, icon: "ri-virus-line", color: "danger" },
            { label: "Vùng có dịch", value: districts.length, icon: "ri-map-pin-2-line", color: "warning" },
            { label: "Ca tăng trong tuần", value: "+8", icon: "ri-arrow-up-line", color: "danger" },
            { label: "Vùng đang giảm", value: 1, icon: "ri-arrow-down-line", color: "success" },
          ].map((s, idx) => (
            <Col md={3} key={idx} className="mb-2">
              <Card className="mb-0">
                <CardBody className="p-3 d-flex align-items-center gap-3">
                  <div className={`bg-${s.color}-subtle rounded d-flex align-items-center justify-content-center`} style={{ width: 40, height: 40 }}>
                    <i className={`${s.icon} text-${s.color} fs-18`}></i>
                  </div>
                  <div>
                    <h5 className="fw-bold mb-0">{s.value}</h5>
                    <p className="text-muted fs-12 mb-0">{s.label}</p>
                  </div>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>

        <Row>
          {/* Map Visualization (SVG placeholder with district dots) */}
          <Col xl={7} className="mb-3">
            <Card className="h-100">
              <CardBody className="p-4">
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <h6 className="fw-semibold mb-0">Bản đồ phân bố ca bệnh — Đồng Nai</h6>
                  <div className="d-flex gap-2">
                    {Object.entries(severityConfig).map(([key, cfg]) => (
                      <span key={key} className="d-flex align-items-center gap-1 fs-11 text-muted">
                        <span style={{ width: 8, height: 8, borderRadius: "50%", background: cfg.dot, display: "inline-block" }}></span>
                        {cfg.label}
                      </span>
                    ))}
                  </div>
                </div>
                {/* SVG Map Representation */}
                <div
                  className="rounded position-relative d-flex align-items-center justify-content-center"
                  style={{ background: "rgba(45,206,137,0.04)", border: "1px solid rgba(45,206,137,0.15)", minHeight: 320, overflow: "hidden" }}
                >
                  <svg width="100%" height="320" viewBox="0 0 500 320">
                    {/* Simplified Dong Nai province shape */}
                    <path
                      d="M80,60 L180,30 L320,45 L420,80 L440,160 L400,250 L320,290 L220,300 L130,270 L70,200 L60,130 Z"
                      fill="rgba(45,206,137,0.08)"
                      stroke="rgba(45,206,137,0.4)"
                      strokeWidth="2"
                    />
                    <text x="230" y="170" textAnchor="middle" fill="rgba(0,0,0,0.3)" fontSize="13" fontFamily="Inter, sans-serif">
                      Đồng Nai
                    </text>
                    {/* District dots */}
                    {[
                      { x: 230, y: 100, ...districts[0] },
                      { x: 300, y: 200, ...districts[1] },
                      { x: 370, y: 230, ...districts[2] },
                      { x: 180, y: 130, ...districts[3] },
                      { x: 380, y: 100, ...districts[4] },
                    ].map((d) => (
                      <g key={d.id} style={{ cursor: "pointer" }} onClick={() => setSelectedDistrict(districts.find(m => m.id === d.id) || null)}>
                        <circle
                          cx={d.x}
                          cy={d.y}
                          r={Math.max(10, d.cases * 1.5)}
                          fill={severityConfig[d.severity].dot}
                          fillOpacity={0.7}
                          stroke={severityConfig[d.severity].dot}
                          strokeWidth="2"
                        />
                        <text x={d.x} y={d.y + 4} textAnchor="middle" fill="white" fontSize="11" fontWeight="bold" fontFamily="Inter, sans-serif">
                          {d.cases}
                        </text>
                        <text x={d.x} y={d.y + 24} textAnchor="middle" fill="rgba(0,0,0,0.6)" fontSize="10" fontFamily="Inter, sans-serif">
                          {d.name}
                        </text>
                      </g>
                    ))}
                  </svg>
                  {selectedDistrict && (
                    <div
                      className="position-absolute top-0 end-0 m-3 p-3 rounded shadow"
                      style={{ background: "var(--vz-card-bg)", border: "1px solid var(--vz-border-color)", maxWidth: 200 }}
                      id="map-tooltip"
                    >
                      <div className="d-flex justify-content-between mb-1">
                        <strong className="fs-13">{selectedDistrict.name}</strong>
                        <button style={{ background: "none", border: "none", fontSize: 16 }} onClick={() => setSelectedDistrict(null)}>×</button>
                      </div>
                      <p className="text-muted fs-12 mb-1">{selectedDistrict.cases} ca đang theo dõi</p>
                      <p className="text-muted fs-12 mb-0">Cây: {selectedDistrict.crops.join(", ")}</p>
                      <Badge color={severityConfig[selectedDistrict.severity].color} className="mt-2 fs-11">
                        Mức độ: {severityConfig[selectedDistrict.severity].label}
                      </Badge>
                    </div>
                  )}
                </div>
                <p className="text-muted fs-11 mt-2 text-center">
                  <i className="ri-information-line me-1"></i>
                  Kích thước vòng tròn tỷ lệ với số ca · Nhấn vào để xem chi tiết
                </p>
              </CardBody>
            </Card>
          </Col>

          {/* Right Panel */}
          <Col xl={5} className="mb-3">
            <div className="d-flex flex-column gap-3 h-100">
              {/* Recent Alerts */}
              <Card>
                <CardBody className="p-3">
                  <h6 className="fw-semibold mb-3">
                    <i className="ri-alert-line text-danger me-2"></i>
                    Cảnh báo gần đây
                  </h6>
                  {recentAlerts.map((a) => (
                    <div key={a.id} id={a.id} className="d-flex align-items-center gap-3 mb-2 p-2 rounded" style={{ background: "rgba(0,0,0,0.02)" }}>
                      <div
                        style={{ width: 8, height: 8, borderRadius: "50%", background: severityConfig[a.severity].dot, flexShrink: 0 }}
                      ></div>
                      <div className="flex-grow-1">
                        <p className="mb-0 fs-13 fw-medium">{a.disease}</p>
                        <span className="text-muted fs-11">{a.district} · {a.date}</span>
                      </div>
                      <div className="d-flex flex-column align-items-end">
                        <strong className="fs-13">{a.cases}</strong>
                        <span className="text-muted fs-10">ca</span>
                      </div>
                    </div>
                  ))}
                </CardBody>
              </Card>

              {/* Weekly Trend Chart */}
              <Card className="flex-grow-1">
                <CardBody className="p-3">
                  <h6 className="fw-semibold mb-2">Xu hướng theo tuần</h6>
                  <ReactApexChart
                    options={weeklyChartOptions}
                    series={weeklyTrendSeries}
                    type="line"
                    height={180}
                    id="chart-weekly-trend"
                  />
                </CardBody>
              </Card>
            </div>
          </Col>
        </Row>

        {/* Heatmap */}
        <Row>
          <Col>
            <Card>
              <CardBody className="p-4">
                <ReactApexChart
                  options={heatmapOptions}
                  series={heatmapSeries}
                  type="heatmap"
                  height={200}
                  id="chart-heatmap"
                />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
