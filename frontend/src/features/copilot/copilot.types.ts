export const COPILOT_EVENT_TYPES = [
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
] as const;

export type CopilotEventType = (typeof COPILOT_EVENT_TYPES)[number];

export type AbstentionCode =
  | "INSUFFICIENT_EVIDENCE"
  | "CONFLICTING_EVIDENCE"
  | "OUT_OF_DOMAIN"
  | "POLICY_BLOCKED"
  | "PROVIDER_UNAVAILABLE"
  | "VALIDATION_FAILED";

export interface CopilotAbstention {
  code: AbstentionCode;
  user_message: string;
  attempted_sources: number;
  recovery_actions: string[];
  expert_handoff_available: boolean;
}

export interface CopilotCitation {
  document_id: string;
  label?: string;
  quote?: string;
  url?: string;
}

export interface CopilotApproval {
  required: boolean;
  approval_id?: string;
  action_type?: string;
}

export interface CopilotEvent {
  eventId: string;
  sequence: number;
  type: CopilotEventType;
  payload: Record<string, unknown>;
}

export type CopilotPhase =
  | "idle"
  | "connecting"
  | "retrieving"
  | "streaming"
  | "completed"
  | "abstained"
  | "approval"
  | "degraded"
  | "error";

export interface CopilotState {
  phase: CopilotPhase;
  draft: string;
  citations: CopilotCitation[];
  abstention: CopilotAbstention | null;
  approval: CopilotApproval | null;
  error: string | null;
  conversationRevision: number;
  lastEventId: string | null;
  seenEventIds: string[];
}
