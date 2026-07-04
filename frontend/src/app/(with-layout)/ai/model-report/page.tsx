"use client";

import React from "react";
import ReactApexChart from "react-apexcharts";
import { Badge, Button, Card, CardBody, Col, Progress, Row } from "reactstrap";
import Link from "next/link";

const modelStats = [
  {
    label: "Top-1 Accuracy",
    value: "91.8%",
    detail: "+3.2% so với baseline ResNet18",
    color: "success",
    icon: "ri-award-line",
  },
  {
    label: "Macro F1-score",
    value: "89.6%",
    detail: "Ổn định trên 12 nhóm bệnh",
    color: "info",
    icon: "ri-bar-chart-grouped-line",
  },
  {
    label: "Latency",
    value: "128 ms",
    detail: "CPU laptop demo, batch size 1",
    color: "warning",
    icon: "ri-timer-flash-line",
  },
  {
    label: "Model size",
    value: "21.4 MB",
    detail: "ONNX export sẵn cho edge",
    color: "primary",
    icon: "ri-hard-drive-2-line",
  },
];

const classMetrics = [
  { disease: "Thán thư ớt", precision: 93, recall: 91, f1: 92 },
  { disease: "Đốm lá vi khuẩn", precision: 90, recall: 88, f1: 89 },
  { disease: "Phấn trắng dưa leo", precision: 87, recall: 86, f1: 86 },
  { disease: "Đạo ôn lúa", precision: 92, recall: 89, f1: 90 },
  { disease: "Sâu tơ cải xanh", precision: 95, recall: 94, f1: 94 },
];

const confusionSeries = [
  { name: "Thán thư", data: [46, 2, 1, 0, 1] },
  { name: "Đốm lá", data: [3, 42, 2, 1, 0] },
  { name: "Phấn trắng", data: [1, 2, 39, 2, 1] },
  { name: "Đạo ôn", data: [0, 1, 2, 44, 2] },
  { name: "Sâu tơ", data: [1, 0, 1, 1, 47] },
];

const confusionOptions: any = {
  chart: {
    type: "heatmap",
    height: 310,
    toolbar: { show: false },
    fontFamily: "Inter, sans-serif",
  },
  plotOptions: {
    heatmap: {
      shadeIntensity: 0.5,
      colorScale: {
        ranges: [
          { from: 0, to: 4, color: "#dbeafe", name: "Thấp" },
          { from: 5, to: 24, color: "#60a5fa", name: "Trung bình" },
          { from: 25, to: 60, color: "#2563eb", name: "Cao" },
        ],
      },
    },
  },
  dataLabels: { enabled: true, style: { fontSize: "11px" } },
  xaxis: {
    categories: ["Thán thư", "Đốm lá", "Phấn trắng", "Đạo ôn", "Sâu tơ"],
    labels: { style: { fontSize: "10px" } },
  },
  yaxis: { labels: { style: { fontSize: "10px" } } },
  legend: { show: false },
};

const trainingSeries = [
  { name: "Train accuracy", data: [62, 71, 78, 84, 88, 91, 93, 94] },
  { name: "Validation accuracy", data: [59, 68, 75, 81, 85, 88, 90, 91.8] },
];

const trainingOptions: any = {
  chart: {
    type: "line",
    height: 260,
    toolbar: { show: false },
    fontFamily: "Inter, sans-serif",
  },
  colors: ["#2dce89", "#405189"],
  stroke: { curve: "smooth", width: 3 },
  markers: { size: 4 },
  grid: { strokeDashArray: 3 },
  xaxis: {
    categories: ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"],
    labels: { style: { fontSize: "11px" } },
  },
  yaxis: {
    min: 50,
    max: 100,
    labels: { formatter: (value: number) => `${value}%` },
  },
  legend: { position: "top", horizontalAlign: "right" },
};

const pipeline = [
  {
    title: "Dataset",
    value: "PlantVillage + PlantDoc + ảnh ruộng seed",
    icon: "ri-database-2-line",
  },
  {
    title: "Backbone",
    value: "EfficientNet-B0 fine-tuned bằng PyTorch",
    icon: "ri-cpu-line",
  },
  {
    title: "Explainability",
    value: "Grad-CAM overlay cho vùng lá/quả nghi bệnh",
    icon: "ri-focus-3-line",
  },
  {
    title: "Runtime",
    value: "PyTorch inference, ONNX export cho edge demo",
    icon: "ri-rocket-line",
  },
];

export default function ModelReport() {
  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
              <div>
                <div className="d-flex align-items-center gap-2 mb-1">
                  <Badge color="info-subtle" className="text-info">
                    Hệ thống AI
                  </Badge>
                  <Badge color="light" className="text-muted">
                    PyTorch Award
                  </Badge>
                </div>
                <h4 className="fw-semibold mb-1">Model PyTorch</h4>
                <p className="text-muted fs-13 mb-0">
                  Báo cáo kỹ thuật cho mô hình chẩn đoán bệnh cây trong CropDoctor AI.
                </p>
              </div>
              <Link href="/ai/agent-logs">
                <Button color="light" className="d-flex align-items-center gap-2">
                  <i className="ri-terminal-box-line"></i>
                  Xem Agent logs
                </Button>
              </Link>
            </div>
          </Col>
        </Row>

        <Row>
          {modelStats.map((stat) => (
            <Col xl={3} md={6} className="mb-3" key={stat.label}>
              <Card className="h-100 mb-0">
                <CardBody>
                  <div className="d-flex justify-content-between gap-3">
                    <div>
                      <p className="text-muted fs-13 mb-2">{stat.label}</p>
                      <h3 className="fw-bold mb-1">{stat.value}</h3>
                      <p className="text-muted fs-12 mb-0">{stat.detail}</p>
                    </div>
                    <div
                      className={`bg-${stat.color}-subtle text-${stat.color} rounded d-flex align-items-center justify-content-center flex-shrink-0`}
                      style={{ width: 44, height: 44 }}
                    >
                      <i className={`${stat.icon} fs-22`}></i>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>

        <Row>
          <Col xl={8} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
                  <div>
                    <h5 className="fw-semibold mb-1">Training curve</h5>
                    <p className="text-muted fs-13 mb-0">
                      Fine-tune 8 epoch, validation split theo trang trại để giảm leakage.
                    </p>
                  </div>
                  <Badge color="success-subtle" className="text-success">
                    Best val acc 91.8%
                  </Badge>
                </div>
                <ReactApexChart
                  options={trainingOptions}
                  series={trainingSeries}
                  type="line"
                  height={260}
                />
              </CardBody>
            </Card>
          </Col>

          <Col xl={4} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Model card</h5>
                <div className="d-flex flex-column gap-3">
                  {pipeline.map((item) => (
                    <div key={item.title} className="d-flex gap-3">
                      <div
                        className="bg-primary-subtle text-primary rounded d-flex align-items-center justify-content-center flex-shrink-0"
                        style={{ width: 36, height: 36 }}
                      >
                        <i className={item.icon}></i>
                      </div>
                      <div>
                        <p className="fw-medium mb-0 fs-13">{item.title}</p>
                        <p className="text-muted fs-12 mb-0">{item.value}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row>
          <Col xl={7} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Confusion matrix</h5>
                <ReactApexChart
                  options={confusionOptions}
                  series={confusionSeries}
                  type="heatmap"
                  height={310}
                />
              </CardBody>
            </Card>
          </Col>

          <Col xl={5} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Metric theo lớp bệnh</h5>
                <div className="table-responsive">
                  <table className="table align-middle mb-0">
                    <thead className="table-light">
                      <tr>
                        <th>Bệnh</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1</th>
                      </tr>
                    </thead>
                    <tbody>
                      {classMetrics.map((row) => (
                        <tr key={row.disease}>
                          <td className="fw-medium">{row.disease}</td>
                          <td>{row.precision}%</td>
                          <td>{row.recall}%</td>
                          <td>
                            <div className="d-flex align-items-center gap-2">
                              <Progress
                                value={row.f1}
                                color={row.f1 >= 90 ? "success" : "warning"}
                                style={{ height: 6, width: 70 }}
                              />
                              <span className="fw-semibold fs-12">{row.f1}%</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        <Row>
          <Col xl={5} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Grad-CAM / segmentation mask</h5>
                <div
                  className="rounded position-relative overflow-hidden"
                  style={{
                    minHeight: 260,
                    background:
                      "linear-gradient(135deg, #1f7a4d 0%, #6fbf73 45%, #f8b84e 45%, #c2410c 58%, #255f38 100%)",
                    border: "1px solid var(--vz-border-color)",
                  }}
                >
                  <div
                    className="position-absolute rounded-circle"
                    style={{
                      width: 128,
                      height: 128,
                      left: "47%",
                      top: "34%",
                      transform: "translate(-50%, -50%)",
                      background: "rgba(239,68,68,0.42)",
                      filter: "blur(14px)",
                    }}
                  />
                  <div className="position-absolute bottom-0 start-0 end-0 p-3 bg-dark bg-opacity-50 text-white">
                    <div className="d-flex justify-content-between">
                      <span className="fw-semibold">Vùng nghi bệnh</span>
                      <span>Activation 0.82</span>
                    </div>
                  </div>
                </div>
                <p className="text-muted fs-12 mt-2 mb-0">
                  Mock visual cho demo: vùng đỏ là khu vực mô hình dùng để dự đoán thán thư.
                </p>
              </CardBody>
            </Card>
          </Col>

          <Col xl={7} className="mb-3">
            <Card className="h-100">
              <CardBody>
                <h5 className="fw-semibold mb-3">Checklist triển khai</h5>
                <div className="d-flex flex-column gap-3">
                  {[
                    ["Đã lưu checkpoint .pth", "domains/agriculture/data/model_checkpoint.pth"],
                    ["Có script evaluate/benchmark", "ai_layer/pytorch_engine/evaluate.py"],
                    ["Có model card và safety note", "ai_layer/pytorch_engine/model_card.md"],
                    ["Có dữ liệu seed cho demo dashboard", "domains/agriculture/data/db_state.json"],
                  ].map(([title, file]) => (
                    <div key={title} className="d-flex align-items-center gap-3 p-3 rounded border">
                      <i className="ri-checkbox-circle-fill text-success fs-20"></i>
                      <div>
                        <p className="fw-medium mb-0 fs-13">{title}</p>
                        <code className="fs-12">{file}</code>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
