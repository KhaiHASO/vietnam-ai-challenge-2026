import { describe, expect, test, vi } from "vitest";

import {
  streamCopilotMessage,
  streamCopilotMessageWithReconnect,
} from "../copilot-api";

function sseResponse(frames: string[]): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      frames.forEach(frame => controller.enqueue(encoder.encode(frame)));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "content-type": "text/event-stream" },
  });
}

describe("Copilot SSE client", () => {
  test("parses frames split across network chunks and preserves resume headers", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(
        sseResponse([
          "id: evt-1\nevent: token.delta\nda",
          'ta: {"text":"Lúa"}\n\nid: evt-2\nevent: message.completed\ndata: {"status":"answered","answer":"Lúa"}\n\n',
        ])
      );
    const events: string[] = [];
    await streamCopilotMessage({
      fetchImpl,
      sessionId: "s1",
      accessToken: "access",
      idempotencyKey: "key-1",
      expectedRevision: 2,
      domainId: "agriculture",
      query: "Đạo ôn?",
      lastEventId: "evt-0",
      signal: new AbortController().signal,
      onEvent: event => events.push(`${event.eventId}:${event.type}`),
    });
    expect(events).toEqual(["evt-1:token.delta", "evt-2:message.completed"]);
    expect(fetchImpl).toHaveBeenCalledWith(
      "/api/v1/copilot/sessions/s1/messages",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer access",
          "Idempotency-Key": "key-1",
          "Last-Event-ID": "evt-0",
        }),
      })
    );
    expect(JSON.parse(fetchImpl.mock.calls[0][1].body)).toEqual({
      query: "Đạo ôn?",
      expected_conversation_revision: 2,
      domain_id: "agriculture",
    });
  });

  test("rejects event types outside the public contract", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(
        sseResponse([
          'id: evt-secret\nevent: chain-of-thought\ndata: {"text":"hidden"}\n\n',
        ])
      );
    await expect(
      streamCopilotMessage({
        fetchImpl,
        sessionId: "s1",
        accessToken: "access",
        idempotencyKey: "key-1",
        expectedRevision: 0,
        query: "test",
        domainId: "agriculture",
        signal: new AbortController().signal,
        onEvent: vi.fn(),
      })
    ).rejects.toThrow("Unsupported Copilot event");
  });

  test("reconnects once with the latest received event id after a broken stream", async () => {
    const interrupted = sseResponse([
      'id: evt-1\nevent: message.started\ndata: {"status":"retrieving"}\n\n',
    ]);
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(interrupted)
      .mockResolvedValueOnce(
        sseResponse([
          'id: evt-2\nevent: message.completed\ndata: {"answer":"ok","conversation_revision":1}\n\n',
        ])
      );
    const events: string[] = [];

    await streamCopilotMessageWithReconnect({
      fetchImpl,
      sessionId: "s1",
      accessToken: "access",
      idempotencyKey: "key-1",
      expectedRevision: 0,
      query: "test",
      domainId: "agriculture",
      signal: new AbortController().signal,
      onEvent: event => events.push(event.eventId),
    });

    expect(events).toEqual(["evt-1", "evt-2"]);
    expect(fetchImpl.mock.calls[1][1].headers["Last-Event-ID"]).toBe("evt-1");
  });
});
