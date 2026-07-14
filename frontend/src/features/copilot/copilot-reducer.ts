import type {
  CopilotAbstention,
  CopilotApproval,
  CopilotCitation,
  CopilotEvent,
  CopilotState,
} from "./copilot.types";

export type CopilotAction =
  | { kind: "start" }
  | { kind: "event"; event: CopilotEvent }
  | { kind: "failed"; message: string }
  | { kind: "reset" };

export const initialCopilotState: CopilotState = {
  phase: "idle",
  draft: "",
  citations: [],
  abstention: null,
  approval: null,
  error: null,
  conversationRevision: 0,
  lastEventId: null,
  seenEventIds: [],
};

function asAbstention(
  payload: Record<string, unknown>
): CopilotAbstention | null {
  const candidate = (payload.abstention ??
    payload) as Partial<CopilotAbstention>;
  if (
    typeof candidate.code !== "string" ||
    typeof candidate.user_message !== "string"
  )
    return null;
  return {
    code: candidate.code as CopilotAbstention["code"],
    user_message: candidate.user_message,
    attempted_sources: Number(candidate.attempted_sources ?? 0),
    recovery_actions: Array.isArray(candidate.recovery_actions)
      ? candidate.recovery_actions.filter(
          (item): item is string => typeof item === "string"
        )
      : [],
    expert_handoff_available: candidate.expert_handoff_available === true,
  };
}

function asCitation(payload: Record<string, unknown>): CopilotCitation | null {
  const candidate = (payload.citation ??
    payload) as Partial<CopilotCitation> & {
    chunk_id?: unknown;
    inline_reference?: unknown;
  };
  const documentId =
    typeof candidate.document_id === "string"
      ? candidate.document_id
      : typeof candidate.chunk_id === "string"
        ? candidate.chunk_id
        : null;
  return documentId
    ? {
        document_id: documentId,
        ...(typeof candidate.label === "string"
          ? { label: candidate.label }
          : typeof candidate.inline_reference === "string"
            ? { label: candidate.inline_reference }
            : {}),
        ...(typeof candidate.quote === "string"
          ? { quote: candidate.quote }
          : {}),
        ...(typeof candidate.url === "string" ? { url: candidate.url } : {}),
      }
    : null;
}

function asApproval(payload: Record<string, unknown>): CopilotApproval | null {
  const candidate = (payload.approval ?? payload) as Partial<CopilotApproval>;
  if (candidate.required !== true) return null;
  return {
    required: true,
    ...(typeof candidate.approval_id === "string"
      ? { approval_id: candidate.approval_id }
      : {}),
    ...(typeof candidate.action_type === "string"
      ? { action_type: candidate.action_type }
      : {}),
  };
}

export function copilotReducer(
  state: CopilotState,
  action: CopilotAction
): CopilotState {
  if (action.kind === "reset") return initialCopilotState;
  if (action.kind === "start") {
    return {
      ...initialCopilotState,
      phase: "connecting",
      lastEventId: state.lastEventId,
    };
  }
  if (action.kind === "failed")
    return { ...state, phase: "error", error: action.message };
  if (state.seenEventIds.includes(action.event.eventId)) return state;

  const base = {
    ...state,
    lastEventId: action.event.eventId,
    seenEventIds: [...state.seenEventIds, action.event.eventId].slice(-256),
  };
  const { type, payload } = action.event;
  if (type === "message.started")
    return { ...base, phase: "connecting", error: null };
  if (
    type === "retrieval.completed" ||
    type === "route.selected" ||
    type === "memory.loaded"
  ) {
    return { ...base, phase: "retrieving" };
  }
  if (type === "token.delta") {
    return {
      ...base,
      phase: "streaming",
      draft: `${state.draft}${typeof payload.text === "string" ? payload.text : ""}`,
    };
  }
  if (type === "citation.added") {
    const citation = asCitation(payload);
    return citation
      ? { ...base, citations: [...state.citations, citation] }
      : base;
  }
  if (type === "approval.required") {
    const approval = asApproval(payload);
    return approval
      ? { ...base, phase: "approval", approval, error: null }
      : { ...base, phase: "error", error: "Malformed approval response" };
  }
  if (type === "message.abstained") {
    const abstention = asAbstention(payload);
    return abstention
      ? { ...base, phase: "abstained", abstention, error: null }
      : { ...base, phase: "error", error: "Malformed abstention response" };
  }
  if (type === "message.completed") {
    const answer =
      typeof payload.answer === "string" ? payload.answer : state.draft;
    const revision = payload.conversation_revision;
    return {
      ...base,
      phase: payload.provider_degraded === true ? "degraded" : "completed",
      draft: answer,
      error: null,
      ...(typeof revision === "number" &&
      Number.isInteger(revision) &&
      revision >= 0
        ? { conversationRevision: revision }
        : {}),
    };
  }
  return {
    ...base,
    phase: "error",
    error:
      typeof payload.message === "string"
        ? payload.message
        : "Copilot request failed",
  };
}
