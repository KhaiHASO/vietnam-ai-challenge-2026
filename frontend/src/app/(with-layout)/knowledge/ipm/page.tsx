"use client";

import React from "react";
import { Row, Col, Card, CardBody, Badge, Button, Progress } from "reactstrap";
import Link from "next/link";

const ipmPrinciples = [
  {
    id: "ipm-1",
    icon: "ri-eye-line",
    color: "#2563eb",
    title: "Phòng ngừa & Giám sát",
    desc: "Thường xuyên kiểm tra đồng ruộng, phát hiện sâu bệnh sớm trước khi bùng phát.",
    actions: ["Kiểm tra định kỳ 2-3 lần/tuần", "Dùng AI CropDoctor để chẩn đoán sớm", "Ghi nhật ký theo dõi"],
  },
  {
    id: "ipm-2",
    icon: "ri-plant-line",
    color: "#059669",
    title: "Biện pháp canh tác",
    desc: "Tạo điều kiện bất lợi cho sâu bệnh thông qua kỹ thuật canh tác phù hợp.",
    actions: ["Luân canh cây trồng", "Vệ sinh đồng ruộng", "Mật độ trồng phù hợp", "Tưới tiêu hợp lý"],
  },
  {
    id: "ipm-3",
    icon: "ri-bug-line",
    color: "#7c3aed",
    title: "Biện pháp sinh học",
    desc: "Tận dụng thiên địch tự nhiên và chế phẩm sinh học an toàn.",
    actions: ["Bảo vệ thiên địch (nhện, bọ rùa)", "BT (Bacillus thuringiensis)", "Trichoderma chống nấm", "Bẫy pheromone"],
  },
  {
    id: "ipm-4",
    icon: "ri-medicine-bottle-line",
    color: "#dc2626",
    title: "Hóa học — Biện pháp cuối",
    desc: "Chỉ dùng thuốc BVTV khi thực sự cần thiết, đúng ngưỡng phòng trừ.",
    actions: ["Đúng thuốc", "Đúng liều", "Đúng lúc", "Đúng cách"],
  },
];

const fourRightRules = [
  {
    num: "1",
    title: "Đúng thuốc",
    icon: "ri-test-tube-line",
    color: "danger",
    desc: "Chọn thuốc đúng với loại bệnh/sâu. Không dùng thuốc phổ rộng khi không cần thiết.",
  },
  {
    num: "2",
    title: "Đúng liều",
    icon: "ri-scales-3-line",
    color: "warning",
    desc: "Pha đúng nồng độ theo nhãn thuốc. Không tăng liều để 'cho chắc'.",
  },
  {
    num: "3",
    title: "Đúng lúc",
    icon: "ri-time-line",
    color: "success",
    desc: "Phun khi sâu bệnh đạt ngưỡng phòng trừ. Phun buổi sáng sớm hoặc chiều mát.",
  },
  {
    num: "4",
    title: "Đúng cách",
    icon: "ri-spray-line",
    color: "info",
    desc: "Phun đều, đủ lượng nước, đúng kỹ thuật. Bảo hộ lao động đầy đủ.",
  },
];

const whenToCallExpert = [
  "Bệnh lan rộng hơn 30% diện tích",
  "Không giảm sau 5-7 ngày xử lý",
  "Cây chết hàng loạt không rõ nguyên nhân",
  "AI confidence dưới 60%",
  "Bệnh lạ chưa từng gặp trước đây",
  "Đã phun thuốc 3 lần không hiệu quả",
];

export default function IPMPage() {
  return (
    <div className="page-content">
      <div className="container-fluid">
        {/* Hero */}
        <Row className="mb-4">
          <Col>
            <div
              className="rounded p-4"
              style={{
                background: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
                color: "white",
              }}
            >
              <div className="d-flex align-items-center justify-content-between">
                <div>
                  <h3 className="fw-bold mb-2">
                    🛡️ Quản lý Dịch hại Tổng hợp (IPM)
                  </h3>
                  <p className="mb-0 opacity-90">
                    Integrated Pest Management — Phương pháp bảo vệ cây trồng an toàn, bền vững và hiệu quả
                  </p>
                </div>
                <div className="text-end d-none d-md-block">
                  <div style={{ fontSize: 64 }}>🌿</div>
                </div>
              </div>
            </div>
          </Col>
        </Row>

        {/* 4 IPM Principles */}
        <Row className="mb-4">
          <Col>
            <h5 className="fw-semibold mb-3">
              Bốn trụ cột của IPM
              <span className="text-muted fs-14 fw-normal ms-2">
                — Ưu tiên từ trên xuống
              </span>
            </h5>
          </Col>
        </Row>
        <Row className="mb-4">
          {ipmPrinciples.map((p, idx) => (
            <Col xl={3} md={6} key={p.id} className="mb-3">
              <Card className="h-100" id={p.id}>
                <CardBody className="p-4">
                  <div className="d-flex align-items-center gap-3 mb-3">
                    <div
                      className="rounded d-flex align-items-center justify-content-center"
                      style={{ width: 44, height: 44, background: `${p.color}18` }}
                    >
                      <i className={`${p.icon} fs-20`} style={{ color: p.color }}></i>
                    </div>
                    <div>
                      <Badge
                        style={{ background: p.color }}
                        className="fs-10 mb-1"
                      >
                        Ưu tiên #{idx + 1}
                      </Badge>
                      <h6 className="fw-bold mb-0">{p.title}</h6>
                    </div>
                  </div>
                  <p className="text-muted fs-13 mb-3">{p.desc}</p>
                  <ul className="list-unstyled mb-0">
                    {p.actions.map((a) => (
                      <li key={a} className="d-flex align-items-center gap-2 mb-1">
                        <i className="ri-check-line text-success fs-14"></i>
                        <span className="fs-12 text-muted">{a}</span>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>

        {/* 4 Đúng */}
        <Row className="mb-4">
          <Col>
            <Card>
              <CardBody className="p-4">
                <h5 className="fw-semibold mb-1">
                  4 Đúng trong sử dụng thuốc BVTV
                </h5>
                <p className="text-muted fs-13 mb-4">
                  Nguyên tắc bắt buộc khi phải dùng thuốc — áp dụng sau cùng trong thang IPM
                </p>
                <Row>
                  {fourRightRules.map((r) => (
                    <Col md={3} key={r.num} className="mb-3" id={`rule-${r.num}`}>
                      <div
                        className="p-4 rounded text-center h-100"
                        style={{
                          border: `2px solid var(--vz-${r.color})`,
                          background: `rgba(var(--vz-${r.color}-rgb), 0.05)`,
                        }}
                      >
                        <div
                          className={`d-flex align-items-center justify-content-center rounded-circle mx-auto mb-3 bg-${r.color}`}
                          style={{ width: 52, height: 52 }}
                        >
                          <i className={`${r.icon} text-white fs-22`}></i>
                        </div>
                        <Badge color={r.color} className="mb-2">
                          Đúng #{r.num}
                        </Badge>
                        <h6 className="fw-bold">{r.title}</h6>
                        <p className="text-muted fs-12 mb-0">{r.desc}</p>
                      </div>
                    </Col>
                  ))}
                </Row>
              </CardBody>
            </Card>
          </Col>
        </Row>

        {/* IPM Pyramid + When to call expert */}
        <Row>
          <Col md={7} className="mb-3">
            <Card className="h-100">
              <CardBody className="p-4">
                <h5 className="fw-semibold mb-3">
                  Thang ưu tiên biện pháp xử lý
                </h5>
                {[
                  { label: "Biện pháp canh tác", pct: 100, color: "success", desc: "Ưu tiên đầu tiên" },
                  { label: "Biện pháp sinh học", pct: 75, color: "info", desc: "Dùng khi biện pháp canh tác chưa đủ" },
                  { label: "Thuốc sinh học / thảo mộc", pct: 50, color: "warning", desc: "Ít độc, thân thiện môi trường" },
                  { label: "Thuốc hóa học chọn lọc", pct: 25, color: "danger", desc: "Chỉ khi đạt ngưỡng phòng trừ" },
                ].map((item) => (
                  <div key={item.label} className="mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <span className="fs-13 fw-medium">{item.label}</span>
                      <span className="fs-12 text-muted">{item.desc}</span>
                    </div>
                    <Progress value={item.pct} color={item.color} style={{ height: 18, borderRadius: 6 }} />
                  </div>
                ))}
              </CardBody>
            </Card>
          </Col>
          <Col md={5} className="mb-3">
            <Card className="h-100">
              <CardBody className="p-4">
                <h5 className="fw-semibold mb-3">
                  <i className="ri-stethoscope-line text-danger me-2"></i>
                  Khi nào cần gọi chuyên gia?
                </h5>
                <p className="text-muted fs-13 mb-3">
                  Đừng chần chừ liên hệ cán bộ khuyến nông hoặc gửi ca lên CropDoctor khi:
                </p>
                {whenToCallExpert.map((item, idx) => (
                  <div key={idx} className="d-flex align-items-start gap-2 mb-2">
                    <div
                      className="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                      style={{ width: 22, height: 22, background: "rgba(239,68,68,0.1)", fontSize: 11, fontWeight: 700, color: "#ef4444" }}
                    >
                      !
                    </div>
                    <span className="fs-13 text-muted">{item}</span>
                  </div>
                ))}
                <div className="mt-4">
                  <Link href="/expert/review">
                    <Button color="danger" block id="btn-send-expert-ipm">
                      <i className="ri-stethoscope-line me-2"></i>
                      Gửi ca cho chuyên gia
                    </Button>
                  </Link>
                </div>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
}
