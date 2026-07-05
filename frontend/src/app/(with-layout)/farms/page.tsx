"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button, Progress } from "reactstrap";
import Link from "next/link";
import axios from "axios";

const farms = [
  {
    id: "farm-001",
    name: "Vườn ớt Trảng Bom",
    location: "Trảng Bom, Đồng Nai",
    area: "2.000 m²",
    crop: "Ớt",
    emoji: "🌶️",
    stage: "Ra hoa",
    stageColor: "success",
    health: 62,
    healthLabel: "Cần chú ý",
    healthColor: "warning",
    activeCases: 2,
    lastCheck: "Hôm nay, 08:30",
    notes: "Phát hiện thán thư, đang theo dõi sát",
  },
  {
    id: "farm-002",
    name: "Ruộng cà Long Thành",
    location: "Long Thành, Đồng Nai",
    area: "3.500 m²",
    crop: "Cà chua",
    emoji: "🍅",
    stage: "Đậu quả",
    stageColor: "info",
    health: 85,
    healthLabel: "Tốt",
    healthColor: "success",
    activeCases: 1,
    lastCheck: "Hôm qua, 16:00",
    notes: "Cây phát triển bình thường, cần theo dõi 1 ca",
  },
  {
    id: "farm-003",
    name: "Vườn dưa Nhơn Trạch",
    location: "Nhơn Trạch, Đồng Nai",
    area: "1.800 m²",
    crop: "Dưa leo",
    emoji: "🥒",
    stage: "Vươn ngọn",
    stageColor: "primary",
    health: 91,
    healthLabel: "Rất tốt",
    healthColor: "success",
    activeCases: 1,
    lastCheck: "02/07/2026",
    notes: "Phấn trắng nhẹ, đang chờ chuyên gia xác nhận",
  },
];

const stageIcons: Record<string, string> = {
  "Ra hoa": "ri-seedling-line",
  "Đậu quả": "ri-leaf-line",
  "Vươn ngọn": "ri-plant-line",
};

export default function Farms() {
  const [farmList, setFarmList] = useState<any[]>([]);

  useEffect(() => {
    const fetchFarms = async () => {
      try {
        const response = await axios.get("/api/farms");
        if (response && response.farms) {
          const backendFarms = response.farms.map((f: any) => ({
            id: f.farm_id,
            name: f.name === "Plot A - Durian" ? "Vườn sầu riêng CRP-304" : f.name === "Plot B - Rice" ? "Ruộng lúa Nhơn Trạch" : f.name,
            location: "Đồng Nai",
            area: f.farm_id === "FRM-501" ? "2.000 m²" : "3.500 m²",
            crop: f.crop_type,
            emoji: f.crop_type.toLowerCase().includes("durian") ? "🥑" : f.crop_type.toLowerCase().includes("rice") ? "🌾" : "🌱",
            stage: f.days_since_last_treatment < 5 ? "Ra hoa" : "Vươn ngọn",
            stageColor: f.days_since_last_treatment < 5 ? "success" : "primary",
            health: Math.round(100 - f.leaf_damage_percent),
            healthLabel: (100 - f.leaf_damage_percent) > 80 ? "Rất tốt" : (100 - f.leaf_damage_percent) > 60 ? "Tốt" : "Cần chú ý",
            healthColor: (100 - f.leaf_damage_percent) > 80 ? "success" : (100 - f.leaf_damage_percent) > 60 ? "success" : "warning",
            activeCases: f.leaf_damage_percent > 30 ? 2 : 1,
            lastCheck: `Hôm qua, 16:00`,
            notes: f.leaf_damage_percent > 30 ? "Phát hiện stress hoặc đốm bệnh rải rác" : "Cây khỏe mạnh bình thường",
          }));
          setFarmList(backendFarms);
        } else {
          setFarmList(farms);
        }
      } catch (err) {
        console.error(err);
        setFarmList(farms);
      }
    };
    fetchFarms();
  }, []);

  const totalAreaVal = farmList.reduce((acc, curr) => acc + parseInt(curr.area.replace(/\./g, "").replace(" m²", "")), 0);
  const totalCasesVal = farmList.reduce((acc, curr) => acc + curr.activeCases, 0);
  const uniqueCrops = new Set(farmList.map((f) => f.crop)).size;

  return (
    <div className="page-content">
      <div className="container-fluid">
        {/* Header */}
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-plant-line text-success me-2"></i>
                  Vườn của tôi
                </h4>
                <p className="text-muted mb-0 fs-13">
                  {farmList.length} vườn · Tổng diện tích {totalAreaVal.toLocaleString("vi-VN")} m² · Đồng Nai
                </p>
              </div>
              <Button color="success" id="btn-add-farm" className="d-flex align-items-center gap-2">
                <i className="ri-add-line"></i>Thêm vườn
              </Button>
            </div>
          </Col>
        </Row>

        {/* Summary Stats */}
        <Row className="mb-3">
          {[
            { label: "Tổng diện tích", value: `${totalAreaVal.toLocaleString("vi-VN")} m²`, icon: "ri-map-2-line", color: "primary" },
            { label: "Ca đang theo dõi", value: `${totalCasesVal} ca`, icon: "ri-heart-pulse-line", color: "danger" },
            { label: "Cây trồng", value: `${uniqueCrops} loại`, icon: "ri-leaf-line", color: "success" },
            { label: "Lần kiểm tra cuối", value: "Hôm nay", icon: "ri-calendar-check-line", color: "info" },
          ].map((s) => (
            <Col md={3} key={s.label} className="mb-2">
              <Card className="mb-0">
                <CardBody className="p-3 d-flex align-items-center gap-3">
                  <div className={`bg-${s.color}-subtle rounded d-flex align-items-center justify-content-center`} style={{ width: 42, height: 42 }}>
                    <i className={`${s.icon} text-${s.color} fs-18`}></i>
                  </div>
                  <div>
                    <h6 className="fw-bold mb-0">{s.value}</h6>
                    <p className="text-muted fs-12 mb-0">{s.label}</p>
                  </div>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>

        {/* Farm Cards */}
        <Row>
          {farmList.map((farm) => (
            <Col xl={4} md={6} key={farm.id} className="mb-3">
              <Card className="h-100" id={farm.id} style={{ transition: "box-shadow 0.2s" }}>
                <CardBody className="p-4">
                  {/* Farm Header */}
                  <div className="d-flex align-items-start justify-content-between mb-3">
                    <div className="d-flex align-items-center gap-3">
                      <div
                        className="rounded d-flex align-items-center justify-content-center"
                        style={{ width: 48, height: 48, background: "rgba(45,206,137,0.1)", fontSize: 28 }}
                      >
                        {farm.emoji}
                      </div>
                      <div>
                        <h6 className="fw-bold mb-0">{farm.name}</h6>
                        <p className="text-muted fs-12 mb-0">
                          <i className="ri-map-pin-line me-1"></i>
                          {farm.location}
                        </p>
                      </div>
                    </div>
                    {farm.activeCases > 0 && (
                      <Badge color="danger" pill>
                        {farm.activeCases} ca
                      </Badge>
                    )}
                  </div>

                  {/* Farm Details */}
                  <div className="d-flex flex-column gap-2 mb-3">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted fs-13">Diện tích</span>
                      <strong className="fs-13">{farm.area}</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span className="text-muted fs-13">Cây trồng</span>
                      <strong className="fs-13">{farm.crop}</strong>
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="text-muted fs-13">Giai đoạn</span>
                      <Badge color={farm.stageColor} className="fs-11">
                        <i className={`${stageIcons[farm.stage]} me-1`}></i>
                        {farm.stage}
                      </Badge>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span className="text-muted fs-13">Kiểm tra</span>
                      <span className="fs-13 text-muted">{farm.lastCheck}</span>
                    </div>
                  </div>

                  {/* Health Bar */}
                  <div className="mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <span className="fs-12 text-muted">Sức khỏe vườn</span>
                      <span className={`fs-12 fw-bold text-${farm.healthColor}`}>
                        {farm.health}% — {farm.healthLabel}
                      </span>
                    </div>
                    <Progress value={farm.health} color={farm.healthColor} style={{ height: 8, borderRadius: 6 }} />
                  </div>

                  {/* Notes */}
                  <p className="fs-12 text-muted mb-3 p-2 rounded" style={{ background: "rgba(0,0,0,0.03)" }}>
                    📝 {farm.notes}
                  </p>

                  {/* Actions */}
                  <div className="d-flex gap-2">
                    <Link href="/diagnosis/new" className="flex-grow-1">
                      <Button color="success" size="sm" block id={`btn-diagnose-${farm.id}`}>
                        <i className="ri-microscope-line me-1"></i>Chẩn đoán
                      </Button>
                    </Link>
                    <Link href="/farm-logs">
                      <Button color="light" size="sm" id={`btn-logs-${farm.id}`}>
                        <i className="ri-book-open-line"></i>
                      </Button>
                    </Link>
                  </div>
                </CardBody>
              </Card>
            </Col>
          ))}

          {/* Add New Farm Card */}
          <Col xl={4} md={6} className="mb-3">
            <Card
              className="h-100 border-dashed d-flex align-items-center justify-content-center"
              style={{ minHeight: 300, cursor: "pointer", borderStyle: "dashed", borderColor: "var(--vz-border-color)" }}
              id="card-add-farm"
            >
              <CardBody className="text-center">
                <div
                  className="rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3"
                  style={{ width: 56, height: 56, background: "rgba(45,206,137,0.1)" }}
                >
                  <i className="ri-add-line text-success fs-28"></i>
                </div>
                <p className="fw-semibold mb-1">Thêm vườn mới</p>
                <p className="text-muted fs-13">Quản lý thêm vườn canh tác</p>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
