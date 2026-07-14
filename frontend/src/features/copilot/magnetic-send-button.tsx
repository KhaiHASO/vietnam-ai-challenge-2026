"use client";

import { PaperPlaneTilt } from "@phosphor-icons/react";
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
} from "framer-motion";
import type { PointerEvent } from "react";

export function MagneticSendButton({ disabled }: { disabled: boolean }) {
  const reducedMotion = useReducedMotion();
  const offsetX = useMotionValue(0);
  const offsetY = useMotionValue(0);
  const x = useSpring(offsetX, { stiffness: 100, damping: 20 });
  const y = useSpring(offsetY, { stiffness: 100, damping: 20 });

  function move(event: PointerEvent<HTMLButtonElement>) {
    if (reducedMotion || disabled) return;
    const bounds = event.currentTarget.getBoundingClientRect();
    offsetX.set((event.clientX - (bounds.left + bounds.width / 2)) * 0.16);
    offsetY.set((event.clientY - (bounds.top + bounds.height / 2)) * 0.16);
  }

  function reset() {
    offsetX.set(0);
    offsetY.set(0);
  }

  return (
    <motion.button
      type="submit"
      disabled={disabled}
      aria-label="Gửi câu hỏi"
      onPointerMove={move}
      onPointerLeave={reset}
      style={reducedMotion ? undefined : { x, y }}
      whileTap={reducedMotion ? undefined : { scale: 0.96 }}
      className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#28765a] text-white transition-colors hover:bg-[#1d6147] disabled:cursor-not-allowed disabled:bg-[#b6c1b9]"
    >
      <PaperPlaneTilt size={19} weight="fill" />
    </motion.button>
  );
}
