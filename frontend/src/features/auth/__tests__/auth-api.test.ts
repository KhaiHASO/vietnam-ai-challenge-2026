import { describe, expect, test, vi } from "vitest";

import { BrowserAuthClient } from "../auth-api";

describe("BrowserAuthClient", () => {
  test("coalesces concurrent refresh requests", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "fresh",
          token_type: "bearer",
          expires_in: 900,
        }),
        { status: 200 }
      )
    );
    const client = new BrowserAuthClient(fetchImpl);
    await Promise.all([client.refresh(), client.refresh()]);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});
