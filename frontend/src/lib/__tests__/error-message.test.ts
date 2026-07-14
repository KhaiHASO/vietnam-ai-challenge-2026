import { expect, test } from "vitest";
import { toErrorMessage } from "../error-message";

test("normalizes unknown errors without unsafe property access", () => {
  expect(toErrorMessage(new Error("Mất kết nối"))).toBe("Mất kết nối");
  expect(toErrorMessage("timeout")).toBe("timeout");
  expect(toErrorMessage({ unexpected: true })).toBe(
    "Đã xảy ra lỗi không xác định"
  );
});
