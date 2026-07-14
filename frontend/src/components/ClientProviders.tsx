"use client";

import React from "react";
import { AuthProvider } from "@/features/auth/AuthProvider";
import { Providers } from "@/providers";
import { Toaster } from "react-hot-toast";

export default function ClientProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <AuthProvider>{children}</AuthProvider>
      <Toaster position="top-right" />
    </Providers>
  );
}
