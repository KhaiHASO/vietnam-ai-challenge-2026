"use client";

import { useEffect } from "react";
import { initFakeBackend } from "@/utils/fakeBackendInit";

export default function FakeBackendProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    const authType = process.env.NEXT_PUBLIC_DEFAULT_AUTH || "fake";
    if (authType === "fake") {
      initFakeBackend();
    }
  }, []);

  return <>{children}</>;
}
