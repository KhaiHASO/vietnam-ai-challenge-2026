import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test } from "vitest";

import { AuthProvider, useAuth } from "../AuthProvider";
import type { AuthClient } from "../auth-api";

const client: AuthClient = {
  refresh: async () => ({
    access_token: "memory-only",
    expires_in: 900,
    token_type: "bearer",
  }),
  login: async () => ({
    access_token: "memory-only",
    expires_in: 900,
    token_type: "bearer",
  }),
  logout: async () => undefined,
  me: async () => ({ user_id: "u1", tenant_id: "t1", roles: ["expert"] }),
  authorizedFetch: async () => new Response(),
};

function Probe() {
  const auth = useAuth();
  return (
    <>
      <span>{auth.status}</span>
      <button
        type="button"
        onClick={() =>
          void auth.authorizedFetch("/secure").catch(() => undefined)
        }
      >
        request
      </button>
    </>
  );
}

describe("AuthProvider", () => {
  afterEach(cleanup);

  test("keeps the access token out of localStorage", async () => {
    localStorage.clear();
    render(
      <AuthProvider client={client}>
        <Probe />
      </AuthProvider>
    );
    await screen.findByText("authenticated");
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  test("clears the authenticated state after refresh/session failure", async () => {
    const failingClient: AuthClient = {
      ...client,
      authorizedFetch: async () => {
        throw new Error("session expired");
      },
    };
    render(
      <AuthProvider client={failingClient}>
        <Probe />
      </AuthProvider>
    );
    await screen.findByText("authenticated");
    fireEvent.click(screen.getByRole("button", { name: "request" }));

    await screen.findByText("anonymous");
  });
});
