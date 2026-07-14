export type UserRole = "admin" | "expert" | "operator";

export interface Principal {
  user_id: string;
  tenant_id: string;
  roles: UserRole[];
}

export interface AuthSession {
  access_token: string;
  token_type: "bearer" | string;
  expires_in: number;
}

export type AuthStatus = "loading" | "authenticated" | "anonymous";
