"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import CountUp from "react-countup";
import ReactApexChart from "react-apexcharts";
import axios from "axios";
import {
  Badge,
  Button,
  Card,
  CardBody,
  Col,
  Progress,
  Row,
} from "reactstrap";

const kpiData = [
  {
    id: "kpi-follow-up",
    title: "Ca bệnh đang theo dõi",
    value: 7,
    unit: "ca",
    change: "+2 ca hôm nay",
    color: "danger",
    icon: "ri-heart-pulse-line",
    link: "/diagnosis/follow-up",
  },
  {
    id: "kpi-farms",
    title: "Cây trồng quản lý",
    value: 6,
    unit: "loại",
    change: "3 vườn hoạt động",
    color: "success",
    icon: "ri-plant-line",
    link: "/farms",
  },
  {
    id: "kpi-reminders",
    title: "Lịch nhắc hôm nay",
    value: 4,
    unit: "việc",
    change: "2 việc cần xử lý",
    color: "warning",
    icon: "ri-notification-3-line",
    link: "/reminders",
  },
  {
    id: "kpi-model",
    title: "Độ chính xác model",
    value: 91.8,
    unit: "%",
    change: "EfficientNet-B0",
    color: "info",
    icon: "ri-cpu-line",
    link: "/ai/model-report",
    decimals: 1,
  },
];

const recentCases = [
  {
    id: "case-2026-0704-001",
    crop: "Ớt",
    farm: "Vườn ớt Trảng Bom",
    disease: "Thán thư",
    confidence: 89,
    status: "follow-up",
    statusLabel: "Theo dõi 48h",
    date: "04/07/2026",
    owner: "Nguyễn Văn A",
  },
  {
    id: "case-2026-0703-014",
    crop: "Dưa leo",
    farm: "Vườn dưa Nhơn Trạch",
    disease: "Phấn trắng",
    confidence: 61,
    status: "expert",
    statusLabel: "Cần chuyên gia",
    date: "03/07/2026",
    owner: "Tổ HTX Nhơn Trạch",
  },
  {
    id: "case-2026-0702-009",
    crop: "Cà chua",
    farm: "Ruộng cà Long Thành",
    disease: "Đốm lá vi khuẩn",
    confidence: 92,
    status: "resolved",
    statusLabel: "Đã xử lý",
    date: "02/07/2026",
    owner: "Trần Thị B",
  },
  {
    id: "case-2026-0701-004",
    crop: "Lúa",
    farm: "Ruộng lúa Xuân Lộc",
    disease: "Đạo ôn",
    confidence: 83,
    status: "follow-up",
    statusLabel: "Đang giảm",
    date: "01/07/2026",
    owner: "Lê Văn C",
  },
];

const remindersToday = [
  {
    id: "reminder-reshoot",
    time: "08:00",
    title: "Chụp lại ảnh vườn ớt",
    note: "Ca thán thư sau 48h",
    icon: "ri-camera-line",
    color: "danger",
    done: false,
  },
  {
    id: "reminder-irrigation",
    time: "10:30",
    title: "Kiểm tra độ ẩm luống dưa",
    note: "Giảm tưới nếu lá còn ướt",
    icon: "ri-drop-line",
    color: "info",
    done: false,
  },
  {
    id: "reminder-ipm",
    time: "14:00",
    title: "Tỉa lá bệnh và tiêu hủy",
    note: "Không để lại trong vườn",
    icon: "ri-scissors-cut-line",
    color: "success",
    done: false,
  },
  {
    id: "reminder-harvest",
    time: "Hôm nay",
    title: "Hết thời gian cách ly",
    note: "Có thể thu hoạch lô cải xanh",
    icon: "ri-checkbox-circle-line",
    color: "success",
    done: true,
  },
];

const farmHealth = [
  {
    farm: "Vườn ớt Trảng Bom",
    crop: "Ớt",
    health: 62,
    cases: 3,
    color: "warning",
  },
  {
    farm: "Ruộng cà Long Thành",
    crop: "Cà chua",
    health: 84,
    cases: 1,
    color: "success",
  },
  {
    farm: "Vườn dưa Nhơn Trạch",
    crop: "Dưa leo",
    health: 76,
    cases: 2,
    color: "info",
  },
];

const agentPipeline = [
  {
    agent: "Vision Agent",
    result: "Phát hiện đốm nâu lõm trên lá và quả",
    score: "74%",
    icon: "ri-eye-line",
    color: "primary",
  },
  {
    agent: "Context Agent",
    result: "Mưa 3 ngày, độ ẩm cao tại Trảng Bom",
    score: "+12%",
    icon: "ri-cloud-line",
    color: "info",
  },
  {
    agent: "Safety Agent",
    result: "Ưu tiên IPM, chưa khuyến nghị phun thuốc",
    score: "OK",
    icon: "ri-shield-check-line",
    color: "success",
  },
];

const quickRoutes = [
  {
    title: "Chẩn đoán mới",
    text: "Upload ảnh, chọn cây trồng, chạy flow AI Agent.",
    icon: "ri-microscope-line",
    color: "success",
    link: "/diagnosis/new",
  },
  {
    title: "Ca cần theo dõi",
    text: "Các ca cần chụp lại, xác nhận hoặc can thiệp.",
    icon: "ri-loop-right-line",
    color: "warning",
    link: "/diagnosis/follow-up",
  },
  {
    title: "Bản đồ ca bệnh",
    text: "Heatmap ổ dịch theo khu vực cho hợp tác xã.",
    icon: "ri-map-pin-2-line",
    color: "danger",
    link: "/cooperative/map",
  },
  {
    title: "Model PyTorch",
    text: "Accuracy, F1-score, latency, Grad-CAM demo.",
    icon: "ri-cpu-line",
    color: "info",
    link: "/ai/model-report",
  },
];

const cropMixLabels = ["Ot", "Ca chua", "Dua leo", "Lua", "Rau cai"];
const cropMixSeries = [12, 8, 5, 6, 3];

const diseaseTrendSeries = [
  {
    name: "Ca mới",
    data: [3, 5, 2, 8, 4, 6, 7],
  },
  {
    name: "Đã xử lý",
    data: [2, 3, 2, 5, 3, 4, 5],
  },
  {
    name: "Cần chuyên gia",
    data: [1, 1, 0, 2, 1, 2, 3],
  },
];

const diseaseTrendOptions: any = {
  chart: {
    type: "area",
    height: 280,
    toolbar: { show: false },
    fontFamily: "inherit",
  },
  colors: ["#ef4444", "#2dce89", "#f59e0b"],
  dataLabels: { enabled: false },
  stroke: { curve: "smooth", width: 2 },
  fill: {
    type: "gradient",
    gradient: {
      shadeIntensity: 0.9,
      opacityFrom: 0.32,
      opacityTo: 0.06,
    },
  },
  grid: { strokeDashArray: 3 },
  legend: { show: false },
  xaxis: {
    categories: ["28/6", "29/6", "30/6", "01/7", "02/7", "03/7", "04/7"],
    labels: { style: { fontSize: "11px" } },
  },
  yaxis: { labels: { style: { fontSize: "11px" } } },
  tooltip: { shared: true, intersect: false },
};

const cropMixOptions: any = {
  chart: {
    type: "donut",
    height: 230,
    fontFamily: "inherit",
  },
  labels: ["Ớt", "Cà chua", "Dưa leo", "Lúa", "Rau cải"],
  colors: ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#14b8a6"],
  legend: { show: false },
  dataLabels: { enabled: false },
  plotOptions: {
    pie: {
      donut: {
        size: "70%",
        labels: {
          show: true,
          total: {
            show: true,
            label: "Ca bệnh",
            formatter: () => `${cropMixSeries.reduce((sum, value) => sum + value, 0)}`,
          },
        },
      },
    },
  },
};

const statusColor: Record<string, string> = {
  "follow-up": "warning",
  resolved: "success",
  expert: "danger",
};

const statusIcon: Record<string, string> = {
  "follow-up": "ri-time-line",
  resolved: "ri-checkbox-circle-line",
  expert: "ri-alert-line",
};

const confidenceColor = (value: number) => {
  if (value >= 85) return "success";
  if (value >= 70) return "warning";
  return "danger";
};

export default function Dashboard() {
  const [kpis, setKpis] = useState<any[]>(kpiData);
  const [cases, setCases] = useState<any[]>([]);
  const [reminders, setReminders] = useState<any[]>([]);
  const [healthList, setHealthList] = useState<any[]>([]);
  const primaryQuickRoute = quickRoutes[0];
  const secondaryQuickRoutes = quickRoutes.slice(1);
  const diseaseTrendMeta = [
    { label: diseaseTrendSeries[0].name, value: diseaseTrendSeries[0].data.at(-1), color: "danger" },
    { label: diseaseTrendSeries[1].name, value: diseaseTrendSeries[1].data.at(-1), color: "success" },
    { label: diseaseTrendSeries[2].name, value: diseaseTrendSeries[2].data.at(-1), color: "warning" },
  ];
  const cropMixMetaColors = ["danger", "warning", "success", "info", "primary"];
  const cropMixTotal = cropMixSeries.reduce((sum, value) => sum + value, 0);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response: any = await axios.get("/api/dashboard/overview");
        if (response && response.summary) {
          const s = response.summary;
          const updatedKPIs = [...kpiData];
          updatedKPIs[0].value = s.diagnosis_cases || 0;
          updatedKPIs[1].value = s.farms || 0;
          updatedKPIs[2].value = s.active_reminders || 0;
          setKpis(updatedKPIs);

          if (response.recent_cases) {
            const mappedCases = response.recent_cases.map((c: any) => ({
              id: c.case_id,
              crop: c.crop === "ot" ? "Ớt" : c.crop === "tomato" ? "Cà chua" : c.crop.charAt(0).toUpperCase() + c.crop.slice(1),
              farm: c.location || "Vườn local",
              disease: c.summary || "Đang chẩn đoán",
              confidence: c.risk_level === "high" ? 85 : 70,
              status: c.status === "created" ? "follow-up" : c.status || "follow-up",
              statusLabel: c.status === "created" ? "Theo dõi 48h" : c.status === "resolved" ? "Đã xử lý" : "Đang kiểm tra",
              date: new Date(c.created_at).toLocaleDateString("vi-VN"),
              owner: "Nông dân local",
              imageUrl: c.image_url,
            }));
            setCases(mappedCases);
          }
        }
      } catch (err) {
        console.error("Dashboard overview fetch error", err);
      }

      try {
        const responseReminders: any = await axios.get("/api/reminders");
        if (responseReminders && responseReminders.reminders) {
          const mappedReminders = responseReminders.reminders.slice(0, 4).map((r: any) => ({
            id: r.reminder_id,
            time: new Date(r.due_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            title: r.title,
            note: r.notes || r.title,
            icon: r.type === "camera" ? "ri-camera-line" : r.type === "watering" ? "ri-drop-line" : "ri-eye-line",
            color: r.priority === "high" ? "danger" : "info",
            done: r.status === "completed",
          }));
          setReminders(mappedReminders);
        }
      } catch (err) {
        console.error("Dashboard reminders fetch error", err);
      }

      try {
        const response: any = await axios.get("/api/farms");
        if (response && response.farms) {
          const mappedHealth = response.farms.map((f: any) => ({
            farm: f.name === "Plot A - Durian" ? "Vườn sầu riêng CRP-304" : f.name === "Plot B - Rice" ? "Ruộng lúa Nhơn Trạch" : f.name,
            crop: f.crop_type,
            health: Math.round(100 - f.leaf_damage_percent),
            cases: f.leaf_damage_percent > 30 ? 2 : 1,
            color: (100 - f.leaf_damage_percent) > 80 ? "success" : "warning",
          }));
          setHealthList(mappedHealth);
        }
      } catch (err) {
        console.error("Dashboard farms fetch error", err);
      }
    };
    fetchDashboardData();
  }, []);

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3 g-3">
          <Col>
            <div className="d-flex flex-column flex-xl-row align-items-xl-end justify-content-between gap-3 gap-xl-4">
              <div className="d-flex flex-column gap-2">
                <div className="d-flex align-items-center gap-2 flex-wrap">
                  <Badge color="success-subtle" className="text-success">
                    CropDoctor AI
                  </Badge>
                  <Badge color="light" className="text-muted">
                    Demo VAIC 2026
                  </Badge>
                </div>
                <h4 className="mb-1 fw-semibold">Tổng quan vận hành</h4>
                <p className="text-muted mb-0 fs-13">
                  Thứ Bảy, 04/07/2026 · Đồng Nai · Theo dõi sâu bệnh theo thời gian thực
                </p>
              </div>
              <div className="d-flex flex-column flex-sm-row align-items-stretch align-items-sm-center justify-content-sm-end gap-2">
                <Link href="/ai/agent-logs">
                  <Button color="light" className="d-inline-flex w-100 align-items-center justify-content-center gap-2">
                    <i className="ri-terminal-box-line"></i>
                    Nhật ký Agent
                  </Button>
                </Link>
                <Link href="/diagnosis/new">
                  <Button color="success" className="d-inline-flex w-100 align-items-center justify-content-center gap-2">
                    <i className="ri-microscope-line"></i>
                    Chẩn đoán mới
                  </Button>
                </Link>
              </div>
            </div>
          </Col>
        </Row>

        <Row className="mb-3 g-3">
          <Col>
            <div className="rounded-4 border border-danger-subtle bg-danger-subtle p-3 p-lg-4">
              <div className="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3">
                <div className="d-flex flex-column gap-2">
                  <div className="d-flex align-items-center gap-2 flex-wrap">
                    <span className="avatar-xs rounded-circle bg-danger d-inline-flex align-items-center justify-content-center flex-shrink-0">
                      <i className="ri-error-warning-line text-white fs-14"></i>
                    </span>
                    <Badge color="danger" className="text-uppercase fw-semibold">
                      Ưu tiên cao
                    </Badge>
                    <span className="text-danger-emphasis fw-medium fs-13">
                      Ổ dịch cần theo dõi
                    </span>
                  </div>
                  <div>
                    <h5 className="fw-semibold mb-1 text-body-emphasis">
                      Cảnh báo ổ dịch thán thư trên ớt tại Trảng Bom
                    </h5>
                    <p className="text-body-secondary mb-0 fs-13">
                      12 ca được ghi nhận trong 7 ngày. AI khuyến nghị tỉa lá bệnh,
                      giảm ẩm, chụp lại ảnh sau 48h và chuyển 2 ca chưa chắc cho chuyên gia.
                    </p>
                  </div>
                </div>
                <Link href="/cooperative/map">
                  <Button color="danger" className="d-inline-flex w-100 w-lg-auto align-items-center justify-content-center gap-2">
                    <i className="ri-map-pin-2-line"></i>
                    Xem bản đồ
                  </Button>
                </Link>
              </div>
            </div>
          </Col>
        </Row>

        <Row className="g-3">
          {kpis.map((kpi, index) => {
            const isPrimaryKpi = index === 0;

            return (
            <Col xl={3} md={6} key={kpi.id} className="mb-3">
              <Link href={kpi.link} className="text-decoration-none">
                <Card
                  className={`card-animate h-100 mb-0 ${isPrimaryKpi ? "border-danger-subtle shadow-sm" : ""}`}
                  id={kpi.id}
                >
                  <CardBody className={isPrimaryKpi ? "p-4" : "p-3"}>
                    <div className="d-flex justify-content-between align-items-start gap-3">
                      <div className="d-flex flex-column gap-1">
                        <p
                          className={`fw-medium mb-0 ${isPrimaryKpi ? "text-body-emphasis fs-12 text-uppercase" : "text-muted fs-13"}`}
                        >
                          {kpi.title}
                        </p>
                        <h3 className={`fw-bold text-body mb-0 ${isPrimaryKpi ? "display-6 lh-1" : ""}`}>
                          <CountUp
                            start={0}
                            end={kpi.value}
                            decimals={kpi.decimals || 0}
                            duration={1.2}
                            suffix={` ${kpi.unit}`}
                          />
                        </h3>
                        <Badge
                          color={`${kpi.color}-subtle`}
                          className={`text-${kpi.color} align-self-start ${isPrimaryKpi ? "mt-2 px-2 py-1 fw-semibold" : "mt-1"}`}
                        >
                          {kpi.change}
                        </Badge>
                      </div>
                      <div
                        className={`${isPrimaryKpi ? "avatar-md rounded-3" : "avatar-sm rounded"} bg-${kpi.color}-subtle d-flex align-items-center justify-content-center flex-shrink-0`}
                      >
                        <i className={`${kpi.icon} text-${kpi.color} fs-22`}></i>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              </Link>
            </Col>
            );
          })}
        </Row>

        <Row className="g-3">
          <Col xl={8} className="mb-3">
            <Card className="h-100 border-0 shadow-sm">
              <CardBody className="p-3 p-lg-4">
                <div className="d-flex flex-column flex-lg-row align-items-lg-start justify-content-between gap-3 mb-4">
                  <div>
                    <Badge color="danger-subtle" className="text-danger mb-2">
                      Disease Trend
                    </Badge>
                    <h5 className="fw-semibold mb-1">Xu hướng ca bệnh 7 ngày</h5>
                    <p className="text-muted fs-13 mb-0">
                      Tổng hợp từ chẩn đoán ảnh, nhật ký mùa vụ và chuyên gia.
                    </p>
                  </div>
                  <Badge color="light" className="text-muted">
                    Đồng Nai · Tuần 27/2026
                  </Badge>
                </div>
                <div className="d-flex flex-wrap gap-2 mb-3">
                  {diseaseTrendMeta.map((item) => (
                    <Badge key={item.label} color={`${item.color}-subtle`} className={`text-${item.color} fw-semibold`}>
                      {item.label}: {item.value}
                    </Badge>
                  ))}
                </div>
                <ReactApexChart
                  options={diseaseTrendOptions}
                  series={diseaseTrendSeries}
                  type="area"
                  height={280}
                />
              </CardBody>
            </Card>
          </Col>

          <Col xl={4} className="mb-3">
            <Card className="h-100 border-0 shadow-sm">
              <CardBody className="p-3 p-lg-4 d-flex flex-column gap-4">
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <h5 className="fw-semibold mb-0">Tỷ trọng cây bị ảnh hưởng</h5>
                  <Link href="/knowledge/diseases" className="fs-12">
                    Tra cứu bệnh
                  </Link>
                </div>
                <div className="d-flex flex-wrap gap-2">
                  <Badge color="light" className="text-muted">
                    Total {cropMixTotal} cases
                  </Badge>
                  <Badge color="danger-subtle" className="text-danger">
                    Top: {cropMixLabels[0]}
                  </Badge>
                </div>
                <ReactApexChart
                  options={cropMixOptions}
                  series={cropMixSeries}
                  type="donut"
                  height={230}
                />
                <div className="d-flex flex-column gap-2">
                  {cropMixLabels.map((label, index) => (
                    <div key={label} className="d-flex align-items-center justify-content-between gap-3 rounded-3 bg-light-subtle px-3 py-2">
                      <div className="d-flex align-items-center gap-2">
                        <span className={`avatar-xxs rounded-circle bg-${cropMixMetaColors[index]} flex-shrink-0`}></span>
                        <span className="fw-medium text-body fs-13">{label}</span>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <span className="text-body-secondary fs-12">{cropMixSeries[index]} cases</span>
                        <Badge color="light" className="text-muted">
                          {Math.round((cropMixSeries[index] / cropMixTotal) * 100)}%
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row className="g-3">
          <Col xl={4} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <h5 className="fw-semibold mb-0">Lịch nhắc hôm nay</h5>
                  <Link href="/reminders" className="fs-12">
                    Xem tất cả
                  </Link>
                </div>
                <div className="d-flex flex-column gap-2">
                  {reminders.map((item) => (
                    <div
                      key={item.id}
                      className={`d-flex gap-3 p-2 rounded ${item.done ? "opacity-50" : ""}`}
                      style={{
                        border: "1px solid var(--vz-border-color)",
                        background: item.done ? "var(--vz-light)" : "transparent",
                      }}
                    >
                      <div
                        className={`bg-${item.color}-subtle text-${item.color} rounded d-flex align-items-center justify-content-center flex-shrink-0`}
                        style={{ width: 36, height: 36 }}
                      >
                        <i className={item.icon}></i>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between gap-2">
                          <p className="fw-medium mb-0 fs-13">{item.title}</p>
                          <span className="text-muted fs-11">{item.time}</span>
                        </div>
                        <p className="text-muted mb-0 fs-12">{item.note}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </Col>

          <Col xl={4} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <div className="d-flex flex-column gap-3">
                  {healthList.map((farm) => (
                    <div key={farm.farm}>
                      <div className="d-flex align-items-center justify-content-between mb-1">
                        <div>
                          <p className="fw-medium mb-0 fs-13">{farm.farm}</p>
                          <p className="text-muted fs-12 mb-0">
                            {farm.crop} · {farm.cases} ca đang theo dõi
                          </p>
                        </div>
                        <span className={`fw-semibold fs-13 text-${farm.color}`}>
                          {farm.health}%
                        </span>
                      </div>
                      <Progress value={farm.health} color={farm.color} style={{ height: 7 }} />
                    </div>
                  ))}
                </div>
                <Link href="/farms">
                  <Button color="light" size="sm" className="mt-4 w-100">
                    Quản lý vườn
                  </Button>
                </Link>
              </CardBody>
            </Card>
          </Col>

          <Col xl={4} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <div className="d-flex align-items-center justify-content-between mb-3">
                  <h5 className="fw-semibold mb-0">AI Agent gần nhất</h5>
                  <Badge color="success-subtle" className="text-success">
                    6 agents
                  </Badge>
                </div>
                <div className="d-flex flex-column gap-3">
                  {agentPipeline.map((agent) => (
                    <div key={agent.agent} className="d-flex gap-3">
                      <div
                        className={`bg-${agent.color}-subtle text-${agent.color} rounded d-flex align-items-center justify-content-center flex-shrink-0`}
                        style={{ width: 36, height: 36 }}
                      >
                        <i className={agent.icon}></i>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between gap-2">
                          <p className="fw-medium mb-0 fs-13">{agent.agent}</p>
                          <span className={`text-${agent.color} fw-semibold fs-12`}>
                            {agent.score}
                          </span>
                        </div>
                        <p className="text-muted mb-0 fs-12">{agent.result}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <Link href="/ai/agent-logs">
                  <Button color="light" size="sm" className="mt-4 w-100">
                    Mở nhật ký Agent
                  </Button>
                </Link>
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row className="g-3">
          <Col xs={12} className="mb-3">
            <div className="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-2">
              <div>
                <h5 className="fw-semibold mb-1 text-body-emphasis">Quick Actions</h5>
                <p className="text-body-secondary fs-13 mb-0">
                  Prioritize common actions to reduce handling time.
                </p>
              </div>
              <Badge color="light" className="text-muted align-self-start align-self-lg-auto">
                4 actions
              </Badge>
            </div>
          </Col>

          <Col xl={5} className="mb-3">
            <Link href={primaryQuickRoute.link} className="text-decoration-none">
              <Card className={`h-100 mb-0 border border-${primaryQuickRoute.color}-subtle bg-${primaryQuickRoute.color}-subtle shadow-sm`}>
                <CardBody className="p-4 d-flex flex-column justify-content-between gap-4 h-100">
                  <div className="d-flex flex-column gap-3">
                    <div className={`avatar-sm rounded-3 bg-${primaryQuickRoute.color} d-inline-flex align-items-center justify-content-center text-white`}>
                      <i className={`${primaryQuickRoute.icon} fs-20`}></i>
                    </div>
                    <div className="d-flex flex-column gap-2">
                      <Badge color={primaryQuickRoute.color} className="align-self-start text-uppercase fw-semibold">
                        Primary CTA
                      </Badge>
                      <div>
                        <h5 className="fw-semibold text-body mb-2">{primaryQuickRoute.title}</h5>
                        <p className="text-body-secondary fs-13 mb-0">{primaryQuickRoute.text}</p>
                      </div>
                    </div>
                  </div>
                  <div className="d-inline-flex align-items-center gap-2 text-success fw-semibold fs-13">
                    <span>Start now</span>
                    <i className="ri-arrow-right-line"></i>
                  </div>
                </CardBody>
              </Card>
            </Link>
          </Col>

          <Col xl={7} className="mb-3">
            <Row className="g-3">
              {secondaryQuickRoutes.map((route) => (
                <Col xl={4} md={4} sm={6} key={route.title} className="mb-3">
                  <Link href={route.link} className="text-decoration-none">
                    <Card className="h-100 mb-0 border-0 shadow-sm">
                      <CardBody className="p-3 d-flex flex-column gap-3 h-100">
                        <div className={`avatar-sm rounded-3 bg-${route.color}-subtle text-${route.color} d-inline-flex align-items-center justify-content-center`}>
                          <i className={`${route.icon} fs-18`}></i>
                        </div>
                        <div className="d-flex flex-column gap-1">
                          <h6 className="fw-semibold text-body mb-0">{route.title}</h6>
                          <p className="text-body-secondary fs-13 mb-0">{route.text}</p>
                        </div>
                        <div className={`d-inline-flex align-items-center gap-2 mt-auto text-${route.color} fw-semibold fs-13`}>
                          <span>Open</span>
                          <i className="ri-arrow-right-up-line"></i>
                        </div>
                      </CardBody>
                    </Card>
                  </Link>
                </Col>
              ))}
            </Row>
          </Col>
        </Row>

        <Row className="g-3">
          <Col>
            <Card className="border-0 shadow-sm">
              <CardBody className="p-3 p-lg-4">
                <div className="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3 mb-4">
                  <div>
                    <Badge color="primary-subtle" className="text-primary mb-2">
                      Recent Activity
                    </Badge>
                    <h5 className="fw-semibold mb-1">Ca chẩn đoán gần đây</h5>
                    <p className="text-muted fs-13 mb-0">
                      Dữ liệu demo cho luồng nông dân, hợp tác xã và chuyên gia.
                    </p>
                  </div>
                  <Link href="/diagnosis/history">
                    <Button color="light" size="sm" className="d-inline-flex align-items-center gap-2 align-self-start align-self-lg-auto">
                      Xem lịch sử
                    </Button>
                  </Link>
                </div>
                <div className="d-flex d-lg-none flex-column gap-3">
                  {cases.length === 0 ? (
                    <div className="rounded-3 border border-dashed border-secondary-subtle bg-light-subtle px-4 py-5 text-center">
                      <div className="avatar-sm mx-auto mb-3">
                        <div className="avatar-title rounded-circle bg-light text-muted">
                          <i className="ri-inbox-archive-line fs-20"></i>
                        </div>
                      </div>
                      <h6 className="fw-semibold text-body mb-1">No recent activity</h6>
                      <p className="text-body-secondary fs-13 mb-0">
                        Recent diagnosis cases will appear here after data is loaded.
                      </p>
                    </div>
                  ) : (
                    cases.map((item, index) => (
                      <div
                        key={item.id}
                        className={`rounded-3 border ${index === 0 ? "border-primary-subtle bg-primary-subtle" : "border-secondary-subtle bg-body"} p-3`}
                      >
                        <div className="d-flex gap-3">
                          <div className={`avatar-sm rounded-circle bg-${statusColor[item.status]}-subtle text-${statusColor[item.status]} d-inline-flex align-items-center justify-content-center flex-shrink-0`}>
                            <i className={`${statusIcon[item.status] || "ri-record-circle-line"} fs-18`}></i>
                          </div>
                          <div className="d-flex flex-column gap-2 flex-grow-1">
                            <div className="d-flex flex-wrap align-items-center gap-2">
                              <span className="fw-semibold text-primary">{item.id}</span>
                              <Badge color={statusColor[item.status]} className="badge-border">
                                {item.statusLabel}
                              </Badge>
                              <span className="text-body-secondary fs-12">{item.date}</span>
                            </div>
                            <div>
                              <h6 className="fw-semibold text-body mb-1">{item.disease}</h6>
                              <p className="text-body-secondary fs-13 mb-0">
                                {item.crop} at {item.farm}
                              </p>
                            </div>
                            <div className="d-flex flex-wrap align-items-center gap-2">
                              <Badge color={`${confidenceColor(item.confidence)}-subtle`} className={`text-${confidenceColor(item.confidence)} fw-semibold`}>
                                {item.confidence}% confidence
                              </Badge>
                              <span className="text-body-secondary fs-13">
                                Reporter: {item.owner}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="d-none d-lg-block table-responsive">
                  <table className="table table-hover align-middle table-nowrap mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Mã ca</th>
                        <th>Cây trồng</th>
                        <th>Vườn</th>
                        <th>Bệnh nghi ngờ</th>
                        <th>Độ tin cậy</th>
                        <th>Trạng thái</th>
                        <th>Người báo cáo</th>
                        <th>Ngày</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cases.length === 0 ? (
                        <tr>
                          <td colSpan={8} className="text-center py-5">
                            <div className="d-flex flex-column align-items-center gap-2">
                              <span className="avatar-sm rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center">
                                <i className="ri-inbox-archive-line fs-20"></i>
                              </span>
                              <div>
                                <p className="fw-semibold text-body mb-1">No recent activity</p>
                                <p className="text-body-secondary fs-13 mb-0">
                                  Recent diagnosis cases will appear here after data is loaded.
                                </p>
                              </div>
                            </div>
                          </td>
                        </tr>
                      ) : (
                        cases.map((item) => (
                        <tr key={item.id} className={item.status === "expert" ? "table-danger" : item.status === "follow-up" ? "table-warning" : ""}>
                          <td>
                            <div className="d-flex flex-column gap-1">
                              <span className="fw-semibold text-primary">{item.id}</span>
                              <span className="text-body-secondary fs-12">{item.date}</span>
                            </div>
                          </td>
                          <td>
                            <div className="d-flex align-items-center gap-2">
                              {item.imageUrl ? (
                                <img
                                  src={item.imageUrl}
                                  alt={item.crop}
                                  className="avatar-xxs rounded object-fit-cover"
                                  style={{ width: 28, height: 28, objectFit: "cover" }}
                                />
                              ) : (
                                <span className="avatar-xxs rounded-circle bg-light text-muted d-inline-flex align-items-center justify-content-center">
                                  <i className="ri-leaf-line fs-12"></i>
                                </span>
                              )}
                              <div className="d-flex flex-column gap-1">
                                <span className="fw-medium text-body">{item.crop}</span>
                                <span className="text-body-secondary fs-12">{item.farm}</span>
                              </div>
                            </div>
                          </td>
                          <td className="text-body-secondary">{item.farm}</td>
                          <td>
                            <div className="d-flex flex-column gap-1">
                              <span className="fw-medium text-body">{item.disease}</span>
                              <span className="text-body-secondary fs-12">Reporter: {item.owner}</span>
                            </div>
                          </td>
                          <td>
                            <div className="d-flex align-items-center gap-2">
                              <Progress
                                value={item.confidence}
                                color={confidenceColor(item.confidence)}
                                className="flex-grow-1"
                              />
                              <span className={`fw-semibold fs-12 text-${confidenceColor(item.confidence)}`}>
                                {item.confidence}%
                              </span>
                            </div>
                          </td>
                          <td>
                            <Badge color={statusColor[item.status]} className="d-inline-flex align-items-center gap-1">
                              <i className={statusIcon[item.status] || "ri-record-circle-line"}></i>
                              {item.statusLabel}
                            </Badge>
                          </td>
                          <td className="text-muted">{item.owner}</td>
                          <td className="text-muted">{item.date}</td>
                        </tr>
                      )))
                      }
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
