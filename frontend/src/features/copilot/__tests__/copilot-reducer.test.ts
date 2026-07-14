import { describe, expect, test } from "vitest";

import { copilotReducer, initialCopilotState } from "../copilot-reducer";
import type { CopilotEvent } from "../copilot.types";

const tokenEvent = (eventId: string, text: string): CopilotEvent => ({
  eventId,
  sequence: 3,
  type: "token.delta",
  payload: { text },
});

describe("copilot reducer", () => {
  test("turns typed abstention into a recoverable terminal state", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-5",
        sequence: 5,
        type: "message.abstained",
        payload: {
          code: "INSUFFICIENT_EVIDENCE",
          user_message: "Tôi chưa có đủ nguồn đáng tin cậy để kết luận.",
          attempted_sources: 2,
          recovery_actions: ["refine_question", "ask_expert"],
          expert_handoff_available: true,
        },
      },
    });
    expect(state.phase).toBe("abstained");
    expect(state.error).toBeNull();
    expect(state.abstention?.code).toBe("INSUFFICIENT_EVIDENCE");
  });

  test("accepts every typed abstention emitted by the backend contract", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-conflict",
        sequence: 6,
        type: "message.abstained",
        payload: {
          code: "CONFLICTING_EVIDENCE",
          user_message: "Các nguồn đang mâu thuẫn.",
          attempted_sources: 2,
          recovery_actions: ["ask_expert"],
          expert_handoff_available: true,
        },
      },
    });

    expect(state.abstention?.code).toBe("CONFLICTING_EVIDENCE");
  });

  test("ignores duplicate SSE events after reconnect", () => {
    const once = copilotReducer(initialCopilotState, {
      kind: "event",
      event: tokenEvent("evt-3", "Lúa"),
    });
    const twice = copilotReducer(once, {
      kind: "event",
      event: tokenEvent("evt-3", "Lúa"),
    });
    expect(twice.draft).toBe("Lúa");
    expect(twice.seenEventIds).toEqual(["evt-3"]);
  });

  test("maps backend chunk identifiers into evidence citations", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-citation",
        sequence: 4,
        type: "citation.added",
        payload: { chunk_id: "chunk-1", inline_reference: "[1]" },
      },
    });

    expect(state.citations).toEqual([{ document_id: "chunk-1", label: "[1]" }]);
  });

  test("uses the server-confirmed revision for the next turn", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-complete",
        sequence: 5,
        type: "message.completed",
        payload: { answer: "Đã xác minh", conversation_revision: 3 },
      },
    });

    expect(state.conversationRevision).toBe(3);
  });

  test("keeps approval metadata distinct from evidence and answers", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-approval",
        sequence: 6,
        type: "approval.required",
        payload: {
          approval: {
            required: true,
            approval_id: "approval-1",
            action_type: "apply_treatment",
          },
        },
      },
    });

    expect(state.phase).toBe("approval");
    expect(state.approval?.action_type).toBe("apply_treatment");
    expect(state.citations).toEqual([]);
  });

  test("marks a completed answer as degraded when the provider used fallback", () => {
    const state = copilotReducer(initialCopilotState, {
      kind: "event",
      event: {
        eventId: "evt-degraded",
        sequence: 7,
        type: "message.completed",
        payload: {
          answer: "Fallback answer",
          conversation_revision: 1,
          provider_degraded: true,
        },
      },
    });

    expect(state.phase).toBe("degraded");
    expect(state.draft).toBe("Fallback answer");
  });

  test("never exposes chain-of-thought as an event type", () => {
    const allowed: CopilotEvent["type"][] = [
      "message.started",
      "route.selected",
      "memory.loaded",
      "retrieval.completed",
      "token.delta",
      "citation.added",
      "approval.required",
      "message.abstained",
      "message.completed",
      "error",
    ];
    expect(allowed).not.toContain("chain-of-thought");
  });
});
