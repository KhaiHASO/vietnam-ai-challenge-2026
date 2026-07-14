export type AuthorizedFetch = (
  input: RequestInfo | URL,
  init?: RequestInit
) => Promise<Response>;

export interface KnowledgeIngestion {
  job_id: string;
  status: string;
  attempts: number;
  last_error: string | null;
}

export interface UploadKnowledgeInput {
  file: File;
  domainId: string;
}

function isKnowledgeIngestion(value: unknown): value is KnowledgeIngestion {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.job_id === "string" &&
    typeof record.status === "string" &&
    (record.attempts === undefined || typeof record.attempts === "number") &&
    (record.last_error === undefined ||
      record.last_error === null ||
      typeof record.last_error === "string")
  );
}

async function readIngestion(response: Response): Promise<KnowledgeIngestion> {
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String(body.detail)
        : `Knowledge ingestion request failed (${response.status})`;
    throw new Error(detail);
  }
  if (!isKnowledgeIngestion(body)) {
    throw new Error("Knowledge ingestion response is invalid");
  }
  return {
    job_id: body.job_id,
    status: body.status,
    attempts: body.attempts ?? 0,
    last_error: body.last_error ?? null,
  };
}

export async function uploadKnowledgeDocument(
  authorizedFetch: AuthorizedFetch,
  input: UploadKnowledgeInput
): Promise<KnowledgeIngestion> {
  const body = new FormData();
  body.set("file", input.file);
  body.set("domain_id", input.domainId);
  return readIngestion(
    await authorizedFetch("/api/v1/knowledge/ingestions", {
      method: "POST",
      body,
    })
  );
}

export async function getKnowledgeIngestion(
  authorizedFetch: AuthorizedFetch,
  jobId: string
): Promise<KnowledgeIngestion> {
  return readIngestion(
    await authorizedFetch(
      `/api/v1/knowledge/ingestions/${encodeURIComponent(jobId)}`,
      { method: "GET" }
    )
  );
}
