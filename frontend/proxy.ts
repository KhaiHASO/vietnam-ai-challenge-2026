import { NextRequest, NextResponse } from "next/server";

import { isProductRoute } from "./src/config/product-routes";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".")
  )
    return NextResponse.next();
  return isProductRoute(pathname)
    ? NextResponse.next()
    : NextResponse.json(
        { error: { code: "NOT_FOUND", message: "Không tìm thấy trang" } },
        { status: 404 }
      );
}

export const config = { matcher: ["/:path*"] };
