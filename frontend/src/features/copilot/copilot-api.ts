import {
  COPILOT_EVENT_TYPES,
  type CopilotEvent,
  type CopilotEventType,
} from "./copilot.types";

type FetchLike = typeof fetch;

export interface StreamCopilotMessageOptions {
  fetchImpl?: FetchLike;
  sessionId: string;
  accessToken: string;
  idempotencyKey: string;
  expectedRevision: number;
  query: string;
  domainId: string;
  lastEventId?: string | null;
  signal: AbortSignal;
  onEvent: (event: CopilotEvent) => void;
}

function isEventType(value: string): value is CopilotEventType {
  return (COPILOT_EVENT_TYPES as readonly string[]).includes(value);
}

function parseFrame(frame: string, sequence: number): CopilotEvent | null {
  const lines = frame.replace(/\r/g, "").split("\n");
  const eventId = lines
    .find(line => line.startsWith("id:"))
    ?.slice(3)
    .trim();
  const type =
    lines
      .find(line => line.startsWith("event:"))
      ?.slice(6)
      .trim() ?? "message";
  const data = lines
    .filter(line => line.startsWith("data:"))
    .map(line => line.slice(5).trim())
    .join("\n");
  if (!eventId && !data) return null;
  if (!isEventType(type)) throw new Error(`Unsupported Copilot event: ${type}`);
  let payload: Record<string, unknown> = {};
  if (data) {
    const parsed: unknown = JSON.parse(data);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed))
      throw new Error("Invalid Copilot event payload");
    payload = parsed as Record<string, unknown>;
  }
  return { eventId: eventId || `event-${sequence}`, sequence, type, payload };
}

export async function streamCopilotMessage(
  options: StreamCopilotMessageOptions
): Promise<void> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const headers: Record<string, string> = {
    Accept: "text/event-stream",
    "Content-Type": "application/json",
    Authorization: `Bearer ${options.accessToken}`,
    "Idempotency-Key": options.idempotencyKey,
  };
  if (options.lastEventId) headers["Last-Event-ID"] = options.lastEventId;
  const response = await fetchImpl(
    `/api/v1/copilot/sessions/${encodeURIComponent(options.sessionId)}/messages`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        query: options.query,
        expected_conversation_revision: options.expectedRevision,
        domain_id: options.domainId,
      }),
      signal: options.signal,
    }
  );
  if (!response.ok)
    throw new Error(`Copilot request failed (${response.status})`);
  if (!response.body)
    throw new Error("Copilot response did not include a stream");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sequence = 0;
  while (true) {
    const next = await reader.read();
    if (next.done) break;
    buffer += decoder.decode(next.value, { stream: true });
    let boundary = buffer.indexOf("\n\n");
    while (boundary >= 0) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const event = parseFrame(frame, ++sequence);
      if (event) options.onEvent(event);
      boundary = buffer.indexOf("\n\n");
    }
  }
  buffer += decoder.decode();
  if (buffer.trim()) {
    const event = parseFrame(buffer, ++sequence);
    if (event) options.onEvent(event);
  }
}

export async function streamCopilotMessageWithReconnect(
  options: StreamCopilotMessageOptions
): Promise<void> {
  let lastEventId = options.lastEventId;
  let terminal = false;
  let lastError: unknown;

  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      await streamCopilotMessage({
        ...options,
        lastEventId,
        onEvent: event => {
          lastEventId = event.eventId;
          terminal ||= [
            "message.completed",
            "message.abstained",
            "approval.required",
          ].includes(event.type);
          options.onEvent(event);
        },
      });
      if (terminal) return;
      lastError = new Error("Copilot stream ended before a terminal event");
    } catch (error) {
      if (options.signal.aborted) throw error;
      lastError = error;
    }
  }
  throw lastError instanceof Error
    ? lastError
    : new Error("Copilot stream could not be resumed");
}
