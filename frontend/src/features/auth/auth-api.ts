import type { AuthSession, Principal } from "./auth.types";

export interface AuthClient {
  login(username: string, password: string): Promise<AuthSession>;
  refresh(): Promise<AuthSession>;
  logout(): Promise<void>;
  me(accessToken: string): Promise<Principal>;
  authorizedFetch(
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response>;
}

type FetchLike = typeof fetch;

export class BrowserAuthClient implements AuthClient {
  private accessToken: string | null = null;
  private refreshInFlight: Promise<AuthSession> | null = null;

  constructor(private readonly fetchImpl: FetchLike = fetch) {}

  private async requestSession(
    path: string,
    body?: Record<string, string>
  ): Promise<AuthSession> {
    const response = await this.fetchImpl(path, {
      method: "POST",
      credentials: "include",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) throw new Error("Phiên đăng nhập không hợp lệ");
    const session = (await response.json()) as AuthSession;
    this.accessToken = session.access_token;
    return session;
  }

  login(username: string, password: string) {
    return this.requestSession("/api/v1/auth/login", { username, password });
  }
  refresh(): Promise<AuthSession> {
    if (!this.refreshInFlight)
      this.refreshInFlight = this.requestSession(
        "/api/v1/auth/refresh"
      ).finally(() => {
        this.refreshInFlight = null;
      });
    return this.refreshInFlight;
  }
  async logout(): Promise<void> {
    await this.fetchImpl("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    this.accessToken = null;
  }
  async me(accessToken: string): Promise<Principal> {
    const response = await this.fetchImpl("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
      credentials: "include",
    });
    if (!response.ok) throw new Error("Không thể xác thực người dùng");
    return response.json() as Promise<Principal>;
  }
  async authorizedFetch(
    input: RequestInfo | URL,
    init: RequestInit = {}
  ): Promise<Response> {
    const withToken = (token: string) =>
      this.fetchImpl(input, {
        ...init,
        credentials: "include",
        headers: { ...init.headers, Authorization: `Bearer ${token}` },
      });
    try {
      const first = await withToken(
        this.accessToken ?? (await this.refresh()).access_token
      );
      if (first.status !== 401) return first;
      return withToken((await this.refresh()).access_token);
    } catch {
      this.accessToken = null;
      throw new Error("Phiên đăng nhập đã hết hạn");
    }
  }
}
