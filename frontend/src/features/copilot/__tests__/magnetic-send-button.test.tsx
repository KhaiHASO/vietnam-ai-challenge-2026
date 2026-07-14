import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { MagneticSendButton } from "../magnetic-send-button";

describe("MagneticSendButton", () => {
  test("keeps a labelled, native submit control available", () => {
    render(<MagneticSendButton disabled={false} />);

    expect(screen.getByRole("button", { name: "Gửi câu hỏi" })).toHaveAttribute(
      "type",
      "submit"
    );
  });
});
