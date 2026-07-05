"use client";

import React, { useState, useEffect } from "react";
import { Row, Col, Card, CardBody, Badge, Button } from "reactstrap";
import axios from "axios";

// Pure backend reminders data loaded dynamically.

const typeColorMap: Record<string, string> = {
  camera: "primary",
  check: "warning",
  watering: "info",
  harvest: "success",
  fertilizer: "success",
  isolation: "danger",
};

export default function Reminders() {
  const [reminderList, setReminderList] = useState<any[]>([]);
  const [done, setDone] = useState<string[]>([]);

  useEffect(() => {
    const fetchReminders = async () => {
      try {
        const response = await axios.get("/api/reminders");
        if (response && response.reminders && response.reminders.length > 0) {
          const backendReminders = response.reminders.map((r: any) => ({
            id: r.reminder_id,
            date: new Date(r.due_at).toLocaleDateString("vi-VN"),
            time: new Date(r.due_at).toLocaleTimeString("vi-VN", { hour: '2-digit', minute: '2-digit' }),
            isToday: new Date(r.due_at).toDateString() === new Date().toDateString(),
            type: r.type || "check",
            typeLabel: r.title,
            typeColor: typeColorMap[r.type] || "warning",
            typeIcon: r.type === "camera" ? "ri-camera-line" : r.type === "watering" ? "ri-drop-line" : "ri-eye-line",
            farm: "Vườn canh tác",
            crop: "🌱 Cây trồng",
            desc: r.notes || r.title,
            done: r.status === "completed",
            urgent: r.priority === "high",
          }));
          setReminderList(backendReminders);
          setDone(backendReminders.filter((r: any) => r.done).map((r: any) => r.id));
        } else {
          setReminderList([]);
        }
      } catch (err) {
        console.error(err);
        setReminderList([]);
      }
    };
    fetchReminders();
  }, []);

  const toggle = (id: string) => {
    setDone((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const todayItems = reminderList.filter((r) => r.isToday);
  const upcomingItems = reminderList.filter((r) => !r.isToday);
  const todayDone = todayItems.filter((r) => done.includes(r.id)).length;

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <h4 className="mb-1 fw-semibold">
                  <i className="ri-notification-3-line text-warning me-2"></i>
                  Lịch nhắc chăm sóc
                </h4>
                <p className="text-muted mb-0 fs-13">
                  Hôm nay: {todayDone}/{todayItems.length} việc đã làm ·{" "}
                  {upcomingItems.length} việc sắp tới
                </p>
              </div>
              <Button color="success" id="btn-add-reminder" className="d-flex align-items-center gap-2">
                <i className="ri-add-line"></i>Thêm nhắc
              </Button>
            </div>
          </Col>
        </Row>

        <Row>
          {/* Today Section */}
          <Col xl={6} className="mb-3">
            <h6 className="fw-semibold mb-3 d-flex align-items-center gap-2">
              <span
                className="rounded px-2 py-1"
                style={{ background: "#405189", color: "white", fontSize: 11 }}
              >
                HÔM NAY
              </span>
              04/07/2026
              <Badge color="light" className="text-muted ms-auto">
                {todayDone}/{todayItems.length}
              </Badge>
            </h6>
            <div className="d-flex flex-column gap-2">
              {todayItems.map((r) => {
                const isDone = done.includes(r.id);
                return (
                  <Card
                    key={r.id}
                    id={r.id}
                    className={`mb-0 ${isDone ? "opacity-60" : ""}`}
                    style={{
                      border: r.urgent && !isDone ? "1px solid rgba(239,68,68,0.3)" : "1px solid var(--vz-border-color)",
                      background: r.urgent && !isDone ? "rgba(239,68,68,0.04)" : "var(--vz-card-bg)",
                      transition: "all 0.2s",
                    }}
                  >
                    <CardBody className="p-3">
                      <div className="d-flex gap-3 align-items-start">
                        <button
                          id={`toggle-${r.id}`}
                          onClick={() => toggle(r.id)}
                          style={{ background: "none", border: "none", padding: 0, flexShrink: 0 }}
                        >
                          <i
                            className={`${isDone ? "ri-checkbox-circle-fill text-success" : "ri-checkbox-blank-circle-line text-muted"} fs-22`}
                          ></i>
                        </button>
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center gap-2 mb-1">
                            <Badge color={r.typeColor} className="fs-11">
                              <i className={`${r.typeIcon} me-1`}></i>
                              {r.typeLabel}
                            </Badge>
                            <span className="text-muted fs-11">{r.time}</span>
                            {r.urgent && !isDone && (
                              <Badge color="danger" className="fs-11">⚡ Cấp bách</Badge>
                            )}
                          </div>
                          <p
                            className="mb-1 fs-13"
                            style={{ textDecoration: isDone ? "line-through" : "none" }}
                          >
                            {r.desc}
                          </p>
                          <span className="text-muted fs-11">
                            {r.crop} · {r.farm}
                          </span>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                );
              })}
            </div>
          </Col>

          {/* Upcoming Section */}
          <Col xl={6} className="mb-3">
            <h6 className="fw-semibold mb-3 d-flex align-items-center gap-2">
              <span
                className="rounded px-2 py-1"
                style={{ background: "var(--vz-secondary)", color: "white", fontSize: 11 }}
              >
                SẮP TỚI
              </span>
              7 ngày tới
            </h6>
            <div className="d-flex flex-column gap-2">
              {upcomingItems.map((r) => (
                <Card key={r.id} id={r.id} className="mb-0">
                  <CardBody className="p-3">
                    <div className="d-flex gap-3 align-items-center">
                      <div
                        className={`bg-${r.typeColor}-subtle rounded d-flex align-items-center justify-content-center`}
                        style={{ width: 36, height: 36, flexShrink: 0 }}
                      >
                        <i className={`${r.typeIcon} text-${r.typeColor} fs-16`}></i>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex align-items-center justify-content-between mb-1">
                          <span className="fw-medium fs-13">{r.typeLabel}</span>
                          <span className="text-muted fs-11">{r.date} · {r.time}</span>
                        </div>
                        <p className="mb-0 text-muted fs-12">{r.desc}</p>
                        <span className="text-muted fs-11">{r.crop} · {r.farm}</span>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </Col>
        </Row>
      </div>
    </div>
  );
}
