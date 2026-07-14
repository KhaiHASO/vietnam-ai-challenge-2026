"use client";

import { useCallback, useEffect, useReducer, useRef } from "react";

import {
  streamCopilotMessageWithReconnect,
  type StreamCopilotMessageOptions,
} from "./copilot-api";
import { copilotReducer, initialCopilotState } from "./copilot-reducer";

type StreamInput = Omit<
  StreamCopilotMessageOptions,
  "signal" | "onEvent" | "lastEventId"
>;

export function useCopilotStream() {
  const [state, dispatch] = useReducer(copilotReducer, initialCopilotState);
  const controllerRef = useRef<AbortController | null>(null);
  const send = useCallback(
    async (input: StreamInput) => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      dispatch({ kind: "start" });
      try {
        await streamCopilotMessageWithReconnect({
          ...input,
          signal: controller.signal,
          lastEventId: state.lastEventId,
          onEvent: event => dispatch({ kind: "event", event }),
        });
      } catch (error) {
        if (!controller.signal.aborted)
          dispatch({
            kind: "failed",
            message:
              error instanceof Error ? error.message : "Copilot request failed",
          });
      }
    },
    [state.lastEventId]
  );
  useEffect(() => () => controllerRef.current?.abort(), []);
  return { state, send, reset: () => dispatch({ kind: "reset" }) };
}
