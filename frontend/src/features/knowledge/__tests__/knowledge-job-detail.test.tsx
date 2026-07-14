import { render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import { AuthProvider } from "@/features/auth/AuthProvider";
import type { AuthClient } from "@/features/auth/auth-api";

import { KnowledgeJobDetail } from "../knowledge-job-detail";

test("renders a completed job without exposing storage internals", async () => {
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
    me: async () => ({ user_id: "u1", tenant_id: "t1", roles: ["expert"] }),
    authorizedFetch: vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          job_id: "job-1",
          status: "completed",
          attempts: 1,
          last_error: null,
        }),
        { headers: { "content-type": "application/json" } }
      )
    ),
  };

  render(
    <AuthProvider client={client}>
      <KnowledgeJobDetail jobId="job-1" />
    </AuthProvider>
  );

  expect(await screen.findByText("Đã sẵn sàng cho AI Copilot")).toBeVisible();
  expect(screen.getByText("job-1")).toBeVisible();
  expect(screen.getByRole("link", { name: "Mở AI Copilot" })).toHaveAttribute(
    "href",
    "/ai-copilot"
  );
  expect(screen.queryByText(/storage_path/i)).not.toBeInTheDocument();
});
