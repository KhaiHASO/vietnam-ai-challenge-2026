import React, { useState } from "react";

const Navdata = () => {
  // Group states
  const [isDiagnosis, setIsDiagnosis] = useState<boolean>(false);
  const [isFarm, setIsFarm] = useState<boolean>(false);
  const [isKnowledge, setIsKnowledge] = useState<boolean>(false);
  const [isCooperative, setIsCooperative] = useState<boolean>(false);
  const [isAI, setIsAI] = useState<boolean>(false);
  const [isSettings, setIsSettings] = useState<boolean>(false);

  const [iscurrentState, setIscurrentState] = useState("Dashboard");

  function updateIconSidebar(e: any) {
    if (e && e.target && e.target.getAttribute("sub-items")) {
      const ul: any = document.getElementById("two-column-menu");
      const iconItems: any = ul.querySelectorAll(".nav-icon.active");
      let activeIconItems = [...iconItems];
      activeIconItems.forEach(item => {
        item.classList.remove("active");
        var id = item.getAttribute("sub-items");
        const getID = document.getElementById(id) as HTMLElement;
        if (getID) getID.classList.remove("show");
      });
    }
  }

  const menuItems: any = [
    // ─── CHÍNH ───────────────────────────────────────────────
    {
      label: "Chính",
      isHeader: true,
    },
    {
      id: "dashboard",
      label: "Tổng quan",
      icon: "ri-home-4-line",
      link: "/dashboard",
    },

    // ─── CHẨN ĐOÁN ──────────────────────────────────────────
    {
      label: "Chẩn đoán",
      isHeader: true,
    },
    {
      id: "diagnosis",
      label: "Chẩn đoán",
      icon: "ri-microscope-line",
      link: "/#",
      stateVariables: isDiagnosis,
      click: function (e: any) {
        e.preventDefault();
        setIsDiagnosis(!isDiagnosis);
        setIscurrentState("Diagnosis");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "diagnosis-new",
          label: "Chẩn đoán mới",
          link: "/diagnosis/new",
          parentId: "diagnosis",
          badgeColor: "success",
          badgeName: "AI",
        },
        {
          id: "diagnosis-history",
          label: "Lịch sử chẩn đoán",
          link: "/diagnosis/history",
          parentId: "diagnosis",
        },
        {
          id: "diagnosis-followup",
          label: "Ca cần theo dõi",
          link: "/diagnosis/follow-up",
          parentId: "diagnosis",
          badgeColor: "danger",
          badgeName: "3",
        },
      ],
    },

    // ─── QUẢN LÝ VƯỜN ───────────────────────────────────────
    {
      label: "Quản lý vườn",
      isHeader: true,
    },
    {
      id: "farm",
      label: "Quản lý vườn",
      icon: "ri-plant-line",
      link: "/#",
      stateVariables: isFarm,
      click: function (e: any) {
        e.preventDefault();
        setIsFarm(!isFarm);
        setIscurrentState("Farm");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "farms",
          label: "Vườn của tôi",
          link: "/farms",
          parentId: "farm",
        },
        {
          id: "farm-logs",
          label: "Nhật ký mùa vụ",
          link: "/farm-logs",
          parentId: "farm",
        },
        {
          id: "reminders",
          label: "Lịch nhắc chăm sóc",
          link: "/reminders",
          parentId: "farm",
        },
      ],
    },

    // ─── TRI THỨC ────────────────────────────────────────────
    {
      label: "Tri thức",
      isHeader: true,
    },
    {
      id: "knowledge",
      label: "Tri thức",
      icon: "ri-book-read-line",
      link: "/#",
      stateVariables: isKnowledge,
      click: function (e: any) {
        e.preventDefault();
        setIsKnowledge(!isKnowledge);
        setIscurrentState("Knowledge");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "diseases",
          label: "Thư viện bệnh cây",
          link: "/knowledge/diseases",
          parentId: "knowledge",
        },
        {
          id: "ipm",
          label: "Khuyến nghị IPM",
          link: "/knowledge/ipm",
          parentId: "knowledge",
        },
      ],
    },

    // ─── HỢP TÁC XÃ ─────────────────────────────────────────
    {
      label: "Hợp tác xã",
      isHeader: true,
    },
    {
      id: "cooperative",
      label: "Hợp tác xã",
      icon: "ri-team-line",
      link: "/#",
      stateVariables: isCooperative,
      click: function (e: any) {
        e.preventDefault();
        setIsCooperative(!isCooperative);
        setIscurrentState("Cooperative");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "disease-map",
          label: "Bản đồ ca bệnh",
          link: "/cooperative/map",
          parentId: "cooperative",
        },
        {
          id: "expert-review",
          label: "Chuyên gia xác nhận",
          link: "/expert/review",
          parentId: "cooperative",
          badgeColor: "warning",
          badgeName: "5",
        },
      ],
    },

    // ─── HỆ THỐNG AI ─────────────────────────────────────────
    {
      label: "Hệ thống AI",
      isHeader: true,
    },
    {
      id: "ai-system",
      label: "Hệ thống AI",
      icon: "ri-cpu-line",
      link: "/#",
      stateVariables: isAI,
      click: function (e: any) {
        e.preventDefault();
        setIsAI(!isAI);
        setIscurrentState("AI");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "model-report",
          label: "Model PyTorch",
          link: "/ai/model-report",
          parentId: "ai-system",
          badgeColor: "info",
          badgeName: "v2",
        },
        {
          id: "agent-logs",
          label: "Nhật ký Agent",
          link: "/ai/agent-logs",
          parentId: "ai-system",
        },
      ],
    },

    // ─── CÀI ĐẶT ─────────────────────────────────────────────
    {
      label: "Cài đặt",
      isHeader: true,
    },
    {
      id: "settings",
      label: "Cài đặt",
      icon: "ri-settings-3-line",
      link: "/#",
      stateVariables: isSettings,
      click: function (e: any) {
        e.preventDefault();
        setIsSettings(!isSettings);
        setIscurrentState("Settings");
        updateIconSidebar(e);
      },
      subItems: [
        {
          id: "profile",
          label: "Hồ sơ",
          link: "/settings/profile",
          parentId: "settings",
        },
        {
          id: "system-settings",
          label: "Cài đặt hệ thống",
          link: "/settings/system",
          parentId: "settings",
        },
      ],
    },
  ];

  return <div>{menuItems}</div>;
};

export default Navdata;
