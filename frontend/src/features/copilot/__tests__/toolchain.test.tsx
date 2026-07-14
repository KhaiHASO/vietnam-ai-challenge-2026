import { render, screen } from "@testing-library/react";
import { Leaf } from "@phosphor-icons/react";
import { describe, expect, test } from "vitest";

describe("Focus Canvas toolchain", () => {
  test("renders the approved icon system", () => {
    render(<Leaf aria-label="Nông nghiệp" size={20} weight="regular" />);
    expect(screen.getByLabelText("Nông nghiệp")).toBeVisible();
  });
});
