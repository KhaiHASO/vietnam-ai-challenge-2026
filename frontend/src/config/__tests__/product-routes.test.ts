import { expect, test } from "vitest";
import { isProductRoute } from "../product-routes";

test("denies template-only routes from the production surface", () => {
  expect(isProductRoute("/ai-copilot")).toBe(true);
  expect(isProductRoute("/ai-operations")).toBe(true);
  expect(isProductRoute("/knowledge")).toBe(true);
  expect(isProductRoute("/knowledge/job-1")).toBe(true);
  expect(isProductRoute("/diagnosis/history")).toBe(true);
  expect(isProductRoute("/apps-crypto-wallet")).toBe(false);
  expect(isProductRoute("/ui/buttons")).toBe(false);
});
