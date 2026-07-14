import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";

import { AuthProvider } from "@/features/auth/AuthProvider";
import type { AuthClient } from "@/features/auth/auth-api";

import { KnowledgeBaseWorkspace } from "../knowledge-base-workspace";

function renderWorkspace(
  roles: Array<"admin" | "expert" | "operator">,
  fetchImpl = vi.fn()
) {
  const client: AuthClient = {
    refresh: async () => ({
      access_token: "access",
      expires_in: 900,
      token_type: "bearer",
    }),
    login: async () => ({
      access_token: "access",
      expires_in: 900,
      token_type: "bearer",
    }),
    logout: async () => undefined,
    me: async () => ({ user_id: "u1", tenant_id: "t1", roles }),
    authorizedFetch: fetchImpl,
  };
  return render(
    <AuthProvider client={client}>
      <KnowledgeBaseWorkspace />
    </AuthProvider>
  );
}

describe("Knowledge Base workspace", () => {
  test("explains upload access to an operator instead of showing a broken submit control", async () => {
    renderWorkspace(["operator"]);

    expect(
      await screen.findByText(
        "Chỉ chuyên gia hoặc quản trị viên mới có thể nạp tri thức."
      )
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: "Bắt đầu index" })
    ).not.toBeInTheDocument();
  });

  test("uploads a TXT document and shows the queued ingestion job", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ job_id: "job-1", status: "queued" }), {
        status: 202,
        headers: { "content-type": "application/json" },
      })
    );
    const user = userEvent.setup();
    renderWorkspace(["expert"], fetchImpl);

    await screen.findByRole("button", { name: "Bắt đầu index" });
    await user.upload(
      screen.getByLabelText("Tệp tri thức"),
      new File(["VietGAP"], "policy.txt", { type: "text/plain" })
    );
    await user.click(screen.getByRole("button", { name: "Bắt đầu index" }));

    expect(await screen.findByText("Đang chờ worker index")).toBeVisible();
    expect(
      screen.getByRole("link", { name: "Xem chi tiết job" })
    ).toHaveAttribute("href", "/knowledge/job-1");
  });
});
