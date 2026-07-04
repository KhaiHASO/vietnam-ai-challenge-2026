"use client";
import React, { useEffect } from "react";
import Link from "next/link";
import SimpleBar from "simplebar-react";

//Import Components
import VerticalLayout from "./VerticalLayouts";
import TwoColumnLayout from "./TwoColumnLayout";
import {
  Container,
  DropdownMenu,
  DropdownToggle,
  UncontrolledDropdown,
} from "reactstrap";
import HorizontalLayout from "./HorizontalLayout";

// CropDoctor AI Logo Component
const CropDoctorLogo = ({ size = "lg" }: { size?: "sm" | "lg" }) => {
  if (size === "sm") {
    return (
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="32" height="32" rx="8" fill="#2dce89" />
        <path
          d="M16 6C16 6 8 10 8 18C8 22.4 11.6 26 16 26C20.4 26 24 22.4 24 18C24 10 16 6 16 6Z"
          fill="white"
          fillOpacity="0.9"
        />
        <path
          d="M16 14C16 14 12 16 12 20C12 22.2 13.8 24 16 24"
          stroke="#2dce89"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <path
          d="M16 14C16 14 20 16 20 20"
          stroke="#16a570"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    );
  }
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <svg
        width="28"
        height="28"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="32" height="32" rx="8" fill="#2dce89" />
        <path
          d="M16 6C16 6 8 10 8 18C8 22.4 11.6 26 16 26C20.4 26 24 22.4 24 18C24 10 16 6 16 6Z"
          fill="white"
          fillOpacity="0.9"
        />
        <path
          d="M16 14C16 14 12 16 12 20C12 22.2 13.8 24 16 24"
          stroke="#2dce89"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <path
          d="M16 14C16 14 20 16 20 20"
          stroke="#16a570"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
      <span
        style={{
          fontWeight: 700,
          fontSize: "15px",
          letterSpacing: "-0.3px",
          color: "var(--vz-sidebar-menu-item-color)",
        }}
      >
        CropDoctor<span style={{ color: "#2dce89" }}> AI</span>
      </span>
    </div>
  );
};

const Sidebar = ({ layoutType }: any) => {
  useEffect(() => {
    const verticalOverlay = document.getElementsByClassName("vertical-overlay");
    if (verticalOverlay?.[0]) {
      verticalOverlay[0].addEventListener("click", () => {
        document.body.classList.remove("vertical-sidebar-enable");
      });
    }
  }, []);

  const addEventListenerOnSmHoverMenu = () => {
    const attr = document.documentElement.getAttribute("data-sidebar-size");
    if (attr === "sm-hover") {
      document.documentElement.setAttribute(
        "data-sidebar-size",
        "sm-hover-active"
      );
    } else {
      document.documentElement.setAttribute("data-sidebar-size", "sm-hover");
    }
  };

  return (
    <React.Fragment>
      <div className="app-menu navbar-menu">
        <div className="navbar-brand-box">
          <Link href="/dashboard" className="logo logo-dark">
            <span className="logo-sm">
              <CropDoctorLogo size="sm" />
            </span>
            <span className="logo-lg">
              <CropDoctorLogo size="lg" />
            </span>
          </Link>

          <Link href="/dashboard" className="logo logo-light">
            <span className="logo-sm">
              <CropDoctorLogo size="sm" />
            </span>
            <span className="logo-lg">
              <CropDoctorLogo size="lg" />
            </span>
          </Link>

          <button
            onClick={addEventListenerOnSmHoverMenu}
            type="button"
            className="btn btn-sm p-0 fs-20 header-item float-end btn-vertical-sm-hover"
            id="vertical-hover"
          >
            <i className="ri-record-circle-line"></i>
          </button>
        </div>

        {/* User Profile */}
        <UncontrolledDropdown className="sidebar-user m-1 rounded">
          <DropdownToggle
            tag="button"
            type="button"
            className="btn material-shadow-none"
            id="page-header-user-dropdown"
          >
            <span className="d-flex align-items-center gap-2">
              <span
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #2dce89 0%, #11998e 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 16,
                  color: "white",
                  flexShrink: 0,
                }}
              >
                NA
              </span>
              <span className="text-start">
                <span className="d-block fw-medium sidebar-user-name-text">
                  Nguyễn Văn A
                </span>
                <span className="d-block fs-14 sidebar-user-name-sub-text">
                  <i className="ri ri-circle-fill fs-10 text-success align-baseline"></i>{" "}
                  <span className="align-middle">Nông dân</span>
                </span>
              </span>
            </span>
          </DropdownToggle>
          <DropdownMenu className="dropdown-menu-end">
            <h6 className="dropdown-header">Xin chào, Nguyễn Văn A!</h6>
            <a className="dropdown-item" href="/settings/profile">
              <i className="mdi mdi-account-circle text-muted fs-16 align-middle me-1"></i>{" "}
              <span className="align-middle">Hồ sơ của tôi</span>
            </a>
            <a className="dropdown-item" href="/reminders">
              <i className="mdi mdi-bell-outline text-muted fs-16 align-middle me-1"></i>{" "}
              <span className="align-middle">Lịch nhắc</span>
            </a>
            <a className="dropdown-item" href="/diagnosis/new">
              <i className="mdi mdi-leaf text-muted fs-16 align-middle me-1"></i>{" "}
              <span className="align-middle">Chẩn đoán mới</span>
            </a>
            <div className="dropdown-divider"></div>
            <a className="dropdown-item" href="/settings/system">
              <i className="mdi mdi-cog-outline text-muted fs-16 align-middle me-1"></i>{" "}
              <span className="align-middle">Cài đặt</span>
            </a>
            <a className="dropdown-item text-danger" href="#">
              <i className="mdi mdi-logout text-danger fs-16 align-middle me-1"></i>{" "}
              <span className="align-middle" data-key="t-logout">
                Đăng xuất
              </span>
            </a>
          </DropdownMenu>
        </UncontrolledDropdown>

        {layoutType === "horizontal" ? (
          <div id="scrollbar">
            <Container fluid>
              <div id="two-column-menu"></div>
              <ul className="navbar-nav" id="navbar-nav">
                <HorizontalLayout />
              </ul>
            </Container>
          </div>
        ) : layoutType === "twocolumn" ? (
          <>
            <TwoColumnLayout layoutType={layoutType} />
            <div className="sidebar-background"></div>
          </>
        ) : (
          <>
            <SimpleBar id="scrollbar" className="h-100">
              <Container fluid>
                <div id="two-column-menu"></div>
                <ul className="navbar-nav" id="navbar-nav">
                  <VerticalLayout layoutType={layoutType} />
                </ul>
              </Container>
            </SimpleBar>
            <div className="sidebar-background"></div>
          </>
        )}
      </div>
      <div className="vertical-overlay"></div>
    </React.Fragment>
  );
};

export default Sidebar;
