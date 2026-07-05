import ClientProviders from "@/components/ClientProviders";
import { Metadata } from "next";
import React from "react";
// import { hkGrotesk } from '@/config/fonts';
import "../assets/scss/themes.scss";
// ApexCharts default styles
import "apexcharts/dist/apexcharts.css";
// Swiper styles
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

export const metadata: Metadata = {
  title: "CropDoctor AI - Trợ lý AI chẩn đoán cây trồng",
  description:
    "CropDoctor AI giúp nông hộ chẩn đoán bệnh cây từ ảnh, triệu chứng, thời tiết và khuyến nghị IPM an toàn.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" suppressHydrationWarning data-qb-installed="true">
      <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" />
      </head>
      <body suppressHydrationWarning={true}>
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  );
}
