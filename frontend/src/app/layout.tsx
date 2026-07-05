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
  title: "CropDoctor AI - AI Crop Diagnosis for Healthier Farms",
  description:
    "CropDoctor AI helps farmers upload crop images, receive AI-assisted diagnosis, get safer IPM recommendations, and track follow-up care.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning data-qb-installed="true">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        />
      </head>
      <body suppressHydrationWarning={true}>
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  );
}
