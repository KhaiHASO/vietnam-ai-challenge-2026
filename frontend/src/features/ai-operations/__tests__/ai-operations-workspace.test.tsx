import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { AiOperationsWorkspace } from "../ai-operations-workspace";

test("shows verified controls and an honest unavailable-observability state", () => {
  render(<AiOperationsWorkspace />);

  expect(screen.getByRole("heading", { name: "AI Operations" })).toBeVisible();
  expect(
    screen.getByText("Không có số liệu vận hành trực tiếp trong phiên này.")
  ).toBeVisible();
  expect(
    screen.getByText("Memory không phải bằng chứng chuyên môn")
  ).toBeVisible();
});
