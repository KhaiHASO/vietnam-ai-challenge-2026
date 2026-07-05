"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button } from "reactstrap";
import axios from "axios";

const logEntries = [
  {
    id: "log-001",
    date: "04/07/2026",
    time: "08:30",
    type: "disease",
    typeLabel: "Phát hiện bệnh",
    typeColor: "danger",
    typeIcon: "ri-virus-line",
    farm: "Vườn ớt Trảng Bom",
    crop: "🌶️ Ớt",
    content: "AI chẩn đoán Thán thư (89% confidence). Đốm nâu xuất hiện trên lá và 2-3 quả non.",
    by: "AI Agent",
  },
  {
    id: "log-002",
    date: "03/07/2026",
    time: "14:00",
    type: "treatment",
    typeLabel: "Xử lý bệnh",
    typeColor: "warning",
    typeIcon: "ri-medicine-bottle-line",
    farm: "Vườn ớt Trảng Bom",
    crop: "🌶️ Ớt",
    content: "Tỉa và tiêu hủy 15 lá bệnh. Giảm tưới 30%. Cải thiện thông gió bằng cách tỉa bớt cành.",
    by: "Nguyễn Văn A",
  },
  {
    id: "log-003",
    date: "02/07/2026",
    time: "09:00",
    type: "check",
    typeLabel: "Kiểm tra theo dõi",
    typeColor: "info",
    typeIcon: "ri-camera-line",
    farm: "Vườn ớt Trảng Bom",
    crop: "🌶️ Ớt",
    content: "Chụp lại ảnh theo dõi. Bệnh có vẻ chưa lan rộng thêm. Tiếp tục theo dõi 48h.",
    by: "Nguyễn Văn A",
  },
  {
    id: "log-004",
    date: "01/07/2026",
    time: "16:30",
    type: "watering",
    typeLabel: "Tưới nước",
    typeColor: "primary",
    typeIcon: "ri-drop-line",
    farm: "Ruộng cà Long Thành",
    crop: "🍅 Cà chua",
    content: "Tưới nhỏ giọt 45 phút. Độ ẩm đất đạt 65%. Cây phát triển bình thường.",
    by: "Nguyễn Văn A",
  },
  {
    id: "log-005",
    date: "30/06/2026",
    time: "07:00",
    type: "disease",
    typeLabel: "Phát hiện bệnh",
    typeColor: "danger",
    typeIcon: "ri-virus-line",
    farm: "Vườn ớt Trảng Bom",
    crop: "🌶️ Ớt",
    content: "AI chẩn đoán Héo xanh vi khuẩn (78% confidence). Phát hiện 4 cây có triệu chứng héo đột ngột.",
    by: "AI Agent",
  },
  {
    id: "log-006",
    date: "29/06/2026",
    time: "10:00",
    type: "fertilizer",
    typeLabel: "Bón phân",
    typeColor: "success",
    typeIcon: "ri-seedling-line",
    farm: "Vườn dưa Nhơn Trạch",
    crop: "🥒 Dưa leo",
    content: "Bón NPK 20-20-15 lần 2. Liều 30g/gốc. Tổng 54kg cho 1.800m².",
    by: "Nguyễn Văn A",
  },
  {
    id: "log-007",
    date: "27/06/2026",
    time: "08:00",
    type: "check",
    typeLabel: "Kiểm tra",
    typeColor: "info",
    typeIcon: "ri-eye-line",
    farm: "Ruộng cà Long Thành",
    crop: "🍅 Cà chua",
    content: "Kiểm tra tổng thể vườn cà. Không phát hiện sâu bệnh mới. Cây đang vào giai đoạn đậu quả tốt.",
    by: "Nguyễn Văn A",
  },
  {
    id: "log-008",
    date: "25/06/2026",
    time: "11:00",
    type: "disease",
    typeLabel: "Phát hiện bệnh",
    typeColor: "danger",
    typeIcon: "ri-virus-line",
    farm: "Ruộng cà Long Thành",
    crop: "🍅 Cà chua",
    content: "AI phát hiện nghi héo rũ Fusarium (55% confidence). Đã gửi chuyên gia xác nhận.",
    by: "AI Agent",
  },
];

const typeOptions = [
  { value: "all", label: "Tất cả" },
  { value: "disease", label: "🦠 Bệnh" },
  { value: "treatment", label: "💊 Xử lý" },
  { value: "check", label: "📷 Kiểm tra" },
  { value: "watering", label: "💧 Tưới" },
  { value: "fertilizer", label: "🌱 Bón phân" },
];

const farmOptions = [
  { value: "all", label: "Tất cả vườn" },
  { value: "Vườn ớt Trảng Bom", label: "🌶️ Vườn ớt Trảng Bom" },
  { value: "Ruộng cà Long Thành", label: "🍅 Ruộng cà Long Thành" },
  { value: "Vườn dưa Nhơn Trạch", label: "🥒 Vườn dưa Nhơn Trạch" },
];

export default function FarmLogs() {
  const [logsList, setLogsList] = useState<any[]>(logEntries);
  const [typeFilter, setTypeFilter] = useState("all");
  const [farmFilter, setFarmFilter] = useState("all");

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get("/api/listing/season-logs");
        if (response.data && response.data.season_logs && response.data.season_logs.length > 0) {
          const backendLogs = response.data.season_logs.map((l: any) => ({
            id: l.log_id,
            date: new Date(l.created_at || new Date()).toLocaleDateString("vi-VN"),
            time: new Date(l.created_at || new Date()).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            type: l.treatment_type === "irrigation" ? "watering" : "treatment",
            typeLabel: l.treatment_type === "irrigation" ? "Tưới nước" : "Can thiệp dịch bệnh",
            typeColor: l.treatment_type === "irrigation" ? "primary" : "warning",
            typeIcon: l.treatment_type === "irrigation" ? "ri-drop-line" : "ri-medicine-bottle-line",
            farm: "Vườn canh tác",
            crop: "🌱 Cây trồng",
            content: l.notes || "Ghi nhận xử lý mùa vụ.",
            by: "Hệ thống / Nông dân",
          }));
          setLogsList([...backendLogs, ...logEntries]);
        } else {
          setLogsList(logEntries);
        }
      } catch (err) {
        console.error(err);
        setLogsList(logEntries);
      }
    };
    fetchLogs();
  }, []);

  const filtered = logsList.filter((l) => {
    const matchType = typeFilter === "all" || l.type === typeFilter;
    const matchFarm = farmFilter === "all" || l.farm === farmFilter;
    return matchType && matchFarm;
  });

  const grouped: Record<string, typeof logEntries> = {};
  filtered.forEach((l) => {
    if (!grouped[l.date]) grouped[l.date] = [];
    grouped[l.date].push(l);
  });

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-book-open-line text-info me-2"></i>
                  Nhật ký mùa vụ
                </h4>
                <p className="text-muted mb-0 fs-13">
                  {filtered.length} bản ghi · 3 vườn
                </p>
              </div>
              <Button color="success" id="btn-add-log" className="d-flex align-items-center gap-2">
                <i className="ri-add-line"></i>Thêm nhật ký
              </Button>
            </div>
          </Col>
        </Row>

        {/* Filters */}
        <Row className="mb-3">
          <Col>
            <Card className="mb-0">
              <CardBody className="p-3">
                <div className="d-flex align-items-center gap-3 flex-wrap">
                  <div className="d-flex gap-2 flex-wrap">
                    {typeOptions.map((t) => (
                      <button
                        key={t.value}
                        id={`type-${t.value}`}
                        onClick={() => setTypeFilter(t.value)}
                        className={`btn btn-sm ${typeFilter === t.value ? "btn-primary" : "btn-light"}`}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>
                  <div>
                    <select
                      id="farm-filter"
                      className="form-select form-select-sm"
                      value={farmFilter}
                      onChange={(e) => setFarmFilter(e.target.value)}
                    >
                      {farmOptions.map((f) => (
                        <option key={f.value} value={f.value}>{f.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>

        {/* Timeline */}
        <Row>
          <Col xl={9}>
            {Object.keys(grouped).length === 0 ? (
              <Card>
                <CardBody className="text-center py-5 text-muted">
                  Không có nhật ký nào phù hợp
                </CardBody>
              </Card>
            ) : (
              Object.entries(grouped).map(([date, entries]) => (
                <div key={date} className="mb-4">
                  <div className="d-flex align-items-center gap-3 mb-3">
                    <div
                      className="rounded px-3 py-1"
                      style={{ background: "var(--vz-primary)", color: "white", fontSize: 12, fontWeight: 600 }}
                    >
                      {date}
                    </div>
                    <div style={{ flex: 1, height: 1, background: "var(--vz-border-color)" }}></div>
                  </div>
                  <div className="timeline-2">
                    {entries.map((log, idx) => (
                      <div
                        key={log.id}
                        id={log.id}
                        className="d-flex gap-3 mb-3"
                        style={{ position: "relative", paddingLeft: 16 }}
                      >
                        {/* Timeline dot */}
                        <div style={{ position: "relative", flexShrink: 0 }}>
                          <div
                            className={`d-flex align-items-center justify-content-center rounded-circle bg-${log.typeColor}`}
                            style={{ width: 36, height: 36, zIndex: 1, position: "relative" }}
                          >
                            <i className={`${log.typeIcon} text-white fs-16`}></i>
                          </div>
                          {idx < entries.length - 1 && (
                            <div
                              style={{
                                position: "absolute",
                                left: "50%",
                                top: 36,
                                bottom: -36,
                                width: 2,
                                background: "var(--vz-border-color)",
                                transform: "translateX(-50%)",
                              }}
                            ></div>
                          )}
                        </div>
                        {/* Content */}
                        <Card className="flex-grow-1 mb-0">
                          <CardBody className="p-3">
                            <div className="d-flex align-items-start justify-content-between mb-2">
                              <div className="d-flex align-items-center gap-2">
                                <Badge color={log.typeColor} className="fs-11">
                                  {log.typeLabel}
                                </Badge>
                                <span className="text-muted fs-12">{log.crop}</span>
                                <span className="text-muted fs-12">·</span>
                                <span className="text-muted fs-12">{log.farm}</span>
                              </div>
                              <span className="text-muted fs-11">{log.time}</span>
                            </div>
                            <p className="mb-1 fs-13">{log.content}</p>
                            <span className="text-muted fs-11">
                              <i className="ri-user-line me-1"></i>
                              {log.by}
                            </span>
                          </CardBody>
                        </Card>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </Col>
          <Col xl={3}>
            <Card>
              <CardBody>
                <h6 className="fw-semibold mb-3">Tóm tắt tháng 7/2026</h6>
                {[
                  { label: "Ca bệnh phát hiện", count: 3, color: "danger" },
                  { label: "Lần xử lý", count: 2, color: "warning" },
                  { label: "Lần kiểm tra", count: 3, color: "info" },
                  { label: "Lần tưới", count: 1, color: "primary" },
                  { label: "Lần bón phân", count: 1, color: "success" },
                ].map((s) => (
                  <div key={s.label} className="d-flex justify-content-between align-items-center mb-2">
                    <span className="fs-13 text-muted">{s.label}</span>
                    <Badge color={s.color}>{s.count}</Badge>
                  </div>
                ))}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
