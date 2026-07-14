import { describe, expect, test, vi } from "vitest";

import {
  getKnowledgeIngestion,
  uploadKnowledgeDocument,
} from "../knowledge-api";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("Knowledge ingestion API", () => {
  test("submits the selected document as multipart without forcing Content-Type", async () => {
    const authorizedFetch = vi
      .fn()
      .mockResolvedValue(
        jsonResponse({ job_id: "job-1", status: "queued" }, 202)
      );
    const file = new File(["VietGAP"], "policy.txt", { type: "text/plain" });

    await uploadKnowledgeDocument(authorizedFetch, {
      file,
      domainId: "agriculture",
    });

    expect(authorizedFetch).toHaveBeenCalledWith(
      "/api/v1/knowledge/ingestions",
      expect.objectContaining({ method: "POST" })
    );
    const [, init] = authorizedFetch.mock.calls[0] as [string, RequestInit];
    expect(init.headers).toBeUndefined();
    expect((init.body as FormData).get("domain_id")).toBe("agriculture");
    expect((init.body as FormData).get("file")).toBe(file);
  });

  test("reads the job status from the scoped ingestion endpoint", async () => {
    const authorizedFetch = vi.fn().mockResolvedValue(
      jsonResponse({
        job_id: "job-1",
        status: "completed",
        attempts: 1,
        last_error: null,
      })
    );

    await expect(
      getKnowledgeIngestion(authorizedFetch, "job-1")
    ).resolves.toMatchObject({
      status: "completed",
    });
    expect(authorizedFetch).toHaveBeenCalledWith(
      "/api/v1/knowledge/ingestions/job-1",
      { method: "GET" }
    );
  });
});
