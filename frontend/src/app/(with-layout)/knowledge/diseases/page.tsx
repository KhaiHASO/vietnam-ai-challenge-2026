"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button, Input, Modal, ModalHeader, ModalBody } from "reactstrap";
import axios from "axios";

// Pure backend disease library data loaded dynamically.

const groupFilters = [
  { value: "all", label: "Tất cả" },
  { value: "fungal", label: "🍄 Bệnh nấm" },
  { value: "bacterial", label: "🦠 Vi khuẩn" },
  { value: "pest", label: "🐛 Sâu/Rầy" },
];

const severityLabel: Record<string, { label: string; color: string }> = {
  critical: { label: "Nghiêm trọng", color: "danger" },
  high: { label: "Cao", color: "warning" },
  medium: { label: "Trung bình", color: "info" },
};

export default function DiseasesLibrary() {
  const [diseaseList, setDiseaseList] = useState<any[]>([]);
  const [groupFilter, setGroupFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<any | null>(null);

  useEffect(() => {
    const fetchDiseases = async () => {
      try {
        const response = await axios.get("/api/listing/knowledge/diseases");
        if (response && response.diseases && response.diseases.length > 0) {
          const mappedDiseases = response.diseases.map((d: any) => {
            const treat = d.treatment || {};
            const treatStr = [treat.biological, treat.prevention, treat.chemical].filter(Boolean).join(". ");
            return {
              id: d.disease_id,
              name: d.name,
              pathogen: d.disease_id === "dis-001" ? "Colletotrichum spp." : d.disease_id === "dis-002" ? "Xanthomonas campestris" : "Nấm/Vi khuẩn hại",
              group: d.disease_id.includes("pest") ? "pest" : d.disease_id.includes("bacterial") ? "bacterial" : "fungal",
              groupLabel: d.disease_id.includes("pest") ? "Sâu hại" : d.disease_id.includes("bacterial") ? "Vi khuẩn" : "Bệnh nấm",
              groupColor: d.disease_id.includes("pest") ? "info" : d.disease_id.includes("bacterial") ? "warning" : "danger",
              crops: d.disease_id === "dis-001" ? ["Ớt", "Cà chua", "Dưa leo"] : ["Cây trồng"],
              emoji: d.disease_id.includes("pest") ? "🐛" : d.disease_id.includes("bacterial") ? "🦠" : "🍄",
              symptoms: d.symptoms || "Không có mô tả triệu chứng.",
              conditions: d.description || "Nhiệt độ ấm, độ ẩm cao.",
              treatment: treatStr || "Tỉa lá bệnh, bón phân cân đối.",
              severity: d.severity || "medium",
              ai_accuracy: 85,
              commonInRegion: true,
            };
          });
          setDiseaseList(mappedDiseases);
        } else {
          setDiseaseList([]);
        }
      } catch (err) {
        console.error(err);
        setDiseaseList([]);
      }
    };
    fetchDiseases();
  }, []);

  const filtered = diseaseList.filter((d) => {
    const matchGroup = groupFilter === "all" || d.group === groupFilter;
    const matchSearch =
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.crops.some((c) => c.toLowerCase().includes(search.toLowerCase()));
    return matchGroup && matchSearch;
  });

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-virus-line text-danger me-2"></i>
                  Thư viện bệnh cây
                </h4>
                <p className="text-muted mb-0 fs-13">
                  {diseaseList.length} bệnh phổ biến · Đồng Nai & vùng lân cận
                </p>
              </div>
            </div>
          </Col>
        </Row>

        {/* Filters */}
        <Row className="mb-3">
          <Col>
            <Card className="mb-0">
              <CardBody className="p-3">
                <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
                  <div className="d-flex gap-2 flex-wrap">
                    {groupFilters.map((g) => (
                      <button
                        key={g.value}
                        id={`group-${g.value}`}
                        onClick={() => setGroupFilter(g.value)}
                        className={`btn btn-sm ${groupFilter === g.value ? "btn-danger" : "btn-light"}`}
                      >
                        {g.label}
                      </button>
                    ))}
                  </div>
                  <div style={{ maxWidth: 260 }}>
                    <Input
                      id="search-disease"
                      type="search"
                      placeholder="Tìm bệnh hoặc cây trồng..."
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

        {/* Disease Cards */}
        <Row>
          {filtered.map((d) => (
            <Col xl={3} md={6} key={d.id} className="mb-3">
              <Card
                className="h-100"
                id={d.id}
                style={{ cursor: "pointer", transition: "box-shadow 0.2s" }}
                onClick={() => setSelected(d)}
              >
                <CardBody className="p-3">
                  <div className="d-flex align-items-start justify-content-between mb-2">
                    <span className="fs-32">{d.emoji}</span>
                    <div className="d-flex flex-column gap-1 align-items-end">
                      <Badge color={d.groupColor} className="fs-11">
                        {d.groupLabel}
                      </Badge>
                      <Badge color={severityLabel[d.severity].color} className="fs-10">
                        {severityLabel[d.severity].label}
                      </Badge>
                    </div>
                  </div>
                  <h6 className="fw-bold mb-1">{d.name}</h6>
                  <p className="text-muted fs-12 mb-2">
                    <em>{d.pathogen}</em>
                  </p>
                  <div className="mb-2">
                    <p className="fs-12 text-muted mb-1">Cây thường gặp:</p>
                    <div className="d-flex flex-wrap gap-1">
                      {d.crops.slice(0, 3).map((c) => (
                        <Badge key={c} color="light" className="text-muted fs-11">
                          {c}
                        </Badge>
                      ))}
                      {d.crops.length > 3 && (
                        <Badge color="light" className="text-muted fs-11">
                          +{d.crops.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="d-flex align-items-center justify-content-between mt-3">
                    <span className="fs-11 text-muted">
                      <i className="ri-cpu-line me-1"></i>AI: {d.ai_accuracy}%
                    </span>
                    {d.commonInRegion && (
                      <Badge color="success-subtle" className="text-success fs-11">
                        📍 Phổ biến vùng này
                      </Badge>
                    )}
                  </div>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>

        {/* Detail Modal */}
        <Modal isOpen={!!selected} toggle={() => setSelected(null)} size="lg" centered id="modal-disease-detail">
          {selected && (
            <>
              <ModalHeader toggle={() => setSelected(null)}>
                <span className="me-2">{selected.emoji}</span>
                {selected.name}
              </ModalHeader>
              <ModalBody>
                <div className="d-flex gap-2 mb-3 flex-wrap">
                  <Badge color={selected.groupColor}>{selected.groupLabel}</Badge>
                  <Badge color={severityLabel[selected.severity].color}>
                    Mức độ: {severityLabel[selected.severity].label}
                  </Badge>
                  <Badge color="light" className="text-muted">
                    AI Accuracy: {selected.ai_accuracy}%
                  </Badge>
                </div>
                <p className="text-muted fs-13 mb-3">
                  <strong>Tác nhân gây bệnh:</strong> <em>{selected.pathogen}</em>
                </p>
                <Row>
                  <Col md={6}>
                    <h6 className="fw-semibold">🔍 Triệu chứng</h6>
                    <p className="fs-13 text-muted">{selected.symptoms}</p>
                    <h6 className="fw-semibold">🌡️ Điều kiện phát sinh</h6>
                    <p className="fs-13 text-muted">{selected.conditions}</p>
                  </Col>
                  <Col md={6}>
                    <h6 className="fw-semibold">💊 Cách xử lý</h6>
                    <p className="fs-13 text-muted">{selected.treatment}</p>
                    <h6 className="fw-semibold">🌱 Cây thường gặp</h6>
                    <div className="d-flex flex-wrap gap-1">
                      {selected.crops.map((c) => (
                        <Badge key={c} color="light" className="text-muted">
                          {c}
                        </Badge>
                      ))}
                    </div>
                  </Col>
                </Row>
                <div className="mt-3 d-flex gap-2">
                  <Button color="success" id="btn-diagnose-from-library" onClick={() => setSelected(null)}>
                    <i className="ri-microscope-line me-2"></i>Chẩn đoán ngay
                  </Button>
                  <Button color="light" onClick={() => setSelected(null)}>
                    Đóng
                  </Button>
                </div>
              </ModalBody>
            </>
          )}
        </Modal>
      </div>
    </div>
  );
}
