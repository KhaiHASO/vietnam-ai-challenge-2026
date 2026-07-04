"use client";

import React, { useState } from "react";
import { Row, Col, Card, CardBody, Badge, Button, Progress, Input, Modal, ModalHeader, ModalBody, ModalFooter } from "reactstrap";

const pendingCases = [
  {
    id: "rev-001",
    emoji: "🌶️",
    crop: "Ớt",
    farm: "Vườn ớt Trảng Bom",
    farmer: "Nguyễn Văn A",
    phone: "0901 234 567",
    aiDisease: "Phấn trắng (Powdery Mildew)",
    aiConfidence: 61,
    symptomAnswer: "Xuất hiện sau mưa, lớp trắng trên lá, chưa lan sang quả",
    date: "01/07/2026",
    status: "pending",
    agents: ["Vision", "Symptom", "Context", "Reasoning"],
  },
  {
    id: "rev-002",
    emoji: "🍅",
    crop: "Cà chua",
    farm: "Ruộng cà Long Thành",
    farmer: "Trần Thị B",
    phone: "0912 345 678",
    aiDisease: "Héo rũ Fusarium",
    aiConfidence: 55,
    symptomAnswer: "Cây héo từ từ, lá vàng dưới trước. Thân cắt ra thấy nâu bên trong",
    date: "25/06/2026",
    status: "pending",
    agents: ["Vision", "Symptom", "Context", "Reasoning", "Safety"],
  },
  {
    id: "rev-003",
    emoji: "🌾",
    crop: "Lúa",
    farm: "Ruộng lúa Nhơn Trạch",
    farmer: "Lê Văn C",
    phone: "0923 456 789",
    aiDisease: "Đạo ôn cổ bông (Neck Blast)",
    aiConfidence: 71,
    symptomAnswer: "Cổ bông thối đen, hạt lép. Xảy ra sau sương mù liên tục",
    date: "20/06/2026",
    status: "confirmed",
    expertNote: "Xác nhận đúng Đạo ôn cổ bông. Khuyến nghị phun Tricyclazole ngay.",
    agents: ["Vision", "Symptom", "Context"],
  },
];

type TabType = "pending" | "confirmed" | "corrected";

export default function ExpertReview() {
  const [tab, setTab] = useState<TabType>("pending");
  const [selected, setSelected] = useState<typeof pendingCases[0] | null>(null);
  const [confirmed, setConfirmed] = useState<string[]>(["rev-003"]);
  const [corrected, setCorrected] = useState<string[]>([]);
  const [noteText, setNoteText] = useState("");

  const allCases = pendingCases;
  const filteredCases = allCases.filter((c) => {
    if (tab === "pending") return !confirmed.includes(c.id) && !corrected.includes(c.id);
    if (tab === "confirmed") return confirmed.includes(c.id);
    if (tab === "corrected") return corrected.includes(c.id);
    return true;
  });

  const pendingCount = allCases.filter((c) => !confirmed.includes(c.id) && !corrected.includes(c.id)).length;
  const confirmedCount = confirmed.length;
  const correctedCount = corrected.length;

  const handleConfirm = (id: string) => {
    setConfirmed([...confirmed, id]);
    setSelected(null);
  };
  const handleCorrect = (id: string) => {
    setCorrected([...corrected, id]);
    setSelected(null);
  };

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-stethoscope-line text-info me-2"></i>
                  Chuyên gia xác nhận
                </h4>
                <p className="text-muted mb-0 fs-13">
                  Human-in-the-loop · {pendingCount} ca chờ xét duyệt
                </p>
              </div>
              <div className="p-2 rounded" style={{ background: "rgba(59,130,246,0.08)", border: "1px solid rgba(59,130,246,0.2)" }}>
                <span className="fs-12 text-primary">
                  <i className="ri-shield-user-line me-1"></i>
                  Chuyên gia: Nguyễn Thị B — BVTV Đồng Nai
                </span>
              </div>
            </div>
          </Col>
        </Row>

        {/* Tabs */}
        <Row className="mb-3">
          <Col>
            <div className="d-flex gap-2">
              {([
                { key: "pending", label: "Chờ duyệt", count: pendingCount, color: "warning" },
                { key: "confirmed", label: "Đã xác nhận", count: confirmedCount, color: "success" },
                { key: "corrected", label: "Đã sửa", count: correctedCount, color: "info" },
              ] as const).map((t) => (
                <button
                  key={t.key}
                  id={`tab-${t.key}`}
                  onClick={() => setTab(t.key)}
                  className={`btn ${tab === t.key ? `btn-${t.color}` : "btn-light"}`}
                >
                  {t.label}{" "}
                  <Badge color={tab === t.key ? "light" : t.color} className={tab === t.key ? `text-${t.color}` : ""}>
                    {t.count}
                  </Badge>
                </button>
              ))}
            </div>
          </Col>
        </Row>

        {/* Case List */}
        <Row>
          {filteredCases.length === 0 ? (
            <Col>
              <Card>
                <CardBody className="text-center py-5">
                  <i className="ri-checkbox-circle-line text-success fs-48 d-block mb-3"></i>
                  <h5 className="fw-semibold">Không có ca nào trong mục này</h5>
                </CardBody>
              </Card>
            </Col>
          ) : (
            filteredCases.map((c) => (
              <Col xl={6} key={c.id} className="mb-3">
                <Card id={c.id}>
                  <CardBody className="p-4">
                    <div className="d-flex align-items-start justify-content-between mb-3">
                      <div className="d-flex align-items-center gap-3">
                        <span className="fs-28">{c.emoji}</span>
                        <div>
                          <h6 className="fw-bold mb-0">{c.crop} — {c.farm}</h6>
                          <span className="text-muted fs-12">
                            <i className="ri-user-line me-1"></i>
                            {c.farmer} · {c.phone}
                          </span>
                        </div>
                      </div>
                      <span className="text-muted fs-12">{c.date}</span>
                    </div>

                    {/* AI Result */}
                    <div className="p-3 rounded mb-3" style={{ background: "rgba(59,130,246,0.06)", border: "1px solid rgba(59,130,246,0.15)" }}>
                      <p className="fs-12 text-muted mb-1">
                        <i className="ri-cpu-line me-1"></i>Kết quả AI đề xuất:
                      </p>
                      <div className="d-flex align-items-center justify-content-between">
                        <strong className="fs-14">{c.aiDisease}</strong>
                        <Badge color={c.aiConfidence >= 75 ? "success" : c.aiConfidence >= 60 ? "warning" : "danger"}>
                          {c.aiConfidence}%
                        </Badge>
                      </div>
                      <Progress value={c.aiConfidence} color={c.aiConfidence >= 75 ? "success" : c.aiConfidence >= 60 ? "warning" : "danger"} style={{ height: 5, marginTop: 6 }} />
                    </div>

                    {/* Symptom answer */}
                    <div className="mb-3">
                      <p className="fs-12 text-muted mb-1">
                        <i className="ri-chat-1-line me-1"></i>Nông dân mô tả:
                      </p>
                      <p className="fs-13 mb-0">"{c.symptomAnswer}"</p>
                    </div>

                    {/* Agent trace */}
                    <div className="d-flex flex-wrap gap-1 mb-3">
                      {c.agents.map((ag) => (
                        <Badge key={ag} color="light" className="text-muted fs-11">
                          <i className="ri-cpu-line me-1"></i>{ag}
                        </Badge>
                      ))}
                    </div>

                    {/* Expert note if confirmed */}
                    {c.status === "confirmed" && c.expertNote && (
                      <div className="p-2 rounded mb-3" style={{ background: "rgba(45,206,137,0.08)", border: "1px solid rgba(45,206,137,0.2)" }}>
                        <p className="fs-12 text-success mb-0">
                          <i className="ri-check-double-line me-1"></i>
                          {c.expertNote}
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    {!confirmed.includes(c.id) && !corrected.includes(c.id) && (
                      <div className="d-flex gap-2">
                        <Button
                          color="success"
                          size="sm"
                          id={`btn-confirm-${c.id}`}
                          onClick={() => handleConfirm(c.id)}
                          className="d-flex align-items-center gap-1"
                        >
                          <i className="ri-check-double-line"></i>Xác nhận đúng
                        </Button>
                        <Button
                          color="warning"
                          size="sm"
                          id={`btn-correct-${c.id}`}
                          onClick={() => setSelected(c)}
                          className="d-flex align-items-center gap-1"
                        >
                          <i className="ri-edit-line"></i>Sửa chẩn đoán
                        </Button>
                        <Button color="light" size="sm" id={`btn-note-${c.id}`} onClick={() => setSelected(c)}>
                          <i className="ri-message-2-line"></i>Ghi chú
                        </Button>
                      </div>
                    )}
                    {confirmed.includes(c.id) && (
                      <Badge color="success" className="fs-12 py-2 px-3">
                        <i className="ri-check-double-line me-1"></i>Đã xác nhận
                      </Badge>
                    )}
                    {corrected.includes(c.id) && (
                      <Badge color="info" className="fs-12 py-2 px-3">
                        <i className="ri-edit-line me-1"></i>Đã sửa chẩn đoán
                      </Badge>
                    )}
                  </CardBody>
                </Card>
              </Col>
            ))
          )}
        </Row>

        {/* Correction/Note Modal */}
        <Modal isOpen={!!selected} toggle={() => setSelected(null)} centered id="modal-expert-action">
          {selected && (
            <>
              <ModalHeader toggle={() => setSelected(null)}>
                Sửa chẩn đoán / Ghi chú — {selected.crop}
              </ModalHeader>
              <ModalBody>
                <div className="mb-3">
                  <label className="form-label fw-medium">Chẩn đoán chính xác</label>
                  <Input type="text" id="input-correct-disease" defaultValue={selected.aiDisease} />
                </div>
                <div className="mb-3">
                  <label className="form-label fw-medium">Ghi chú cho nông dân</label>
                  <textarea
                    id="input-expert-note"
                    className="form-control"
                    rows={4}
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Nhập khuyến nghị cụ thể..."
                  />
                </div>
              </ModalBody>
              <ModalFooter>
                <Button color="info" id="btn-submit-correction" onClick={() => handleCorrect(selected.id)}>
                  <i className="ri-send-plane-line me-2"></i>Gửi xác nhận
                </Button>
                <Button color="light" onClick={() => setSelected(null)}>Hủy</Button>
              </ModalFooter>
            </>
          )}
        </Modal>
      </div>
    </div>
  );
}
