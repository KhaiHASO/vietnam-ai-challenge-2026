const PRODUCT_ROUTE_PATTERNS = [
  /^\/$/,
  /^\/(login|logout|ai-copilot|ai-operations|dashboard|profile|reminders)\/?$/,
  /^\/(farms|farm-logs|expert-review|cooperative-map|model-report|agent-logs)(\/|$)/,
  /^\/diagnosis\/(new|history|follow-up)(\/|$)/,
  /^\/knowledge(\/|$)/,
];

export function isProductRoute(pathname: string): boolean {
  return PRODUCT_ROUTE_PATTERNS.some(pattern => pattern.test(pathname));
}
