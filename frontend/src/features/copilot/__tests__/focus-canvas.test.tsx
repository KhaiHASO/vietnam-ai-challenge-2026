import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { FocusCanvas } from "../focus-canvas";

describe("Focus Canvas", () => {
  test("renders the composable Copilot workspace and its safety fallback", () => {
    render(<FocusCanvas />);
    expect(screen.getByRole("link", { name: "Nạp tri thức" })).toHaveAttribute(
      "href",
      "/knowledge"
    );
    expect(screen.getByRole("link", { name: "AI Operations" })).toHaveAttribute(
      "href",
      "/ai-operations"
    );
    expect(
      screen.getByRole("heading", { name: "AI Copilot" })
    ).toBeInTheDocument();
    expect(screen.getByText("Nguồn bằng chứng")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Gửi câu hỏi" })
    ).toBeInTheDocument();
    expect(
      screen.getByText("Trả lời chỉ được đưa ra khi có bằng chứng phù hợp.")
    ).toBeInTheDocument();
  });
});
