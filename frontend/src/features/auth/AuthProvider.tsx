"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { BrowserAuthClient, type AuthClient } from "./auth-api";
import type {
  AuthSession,
  AuthStatus,
  Principal,
  UserRole,
} from "./auth.types";

interface AuthContextValue {
  status: AuthStatus;
  accessToken: string | null;
  principal: Principal | null;
  login(username: string, password: string): Promise<void>;
  logout(): Promise<void>;
  authorizedFetch(
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response>;
  hasRole(...roles: UserRole[]): boolean;
}
const anonymousContext: AuthContextValue = {
  status: "anonymous",
  accessToken: null,
  principal: null,
  login: async () => {
    throw new Error("AuthProvider is unavailable");
  },
  logout: async () => undefined,
  authorizedFetch: async () => {
    throw new Error("Bạn cần đăng nhập");
  },
  hasRole: () => false,
};
const AuthContext = createContext<AuthContextValue>(anonymousContext);

export function AuthProvider({
  children,
  client,
}: {
  children: ReactNode;
  client?: AuthClient;
}) {
  const [defaultClient] = useState<AuthClient>(() => new BrowserAuthClient());
  const activeClient = client ?? defaultClient;
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [principal, setPrincipal] = useState<Principal | null>(null);
  const applySession = useCallback(
    async (session: AuthSession) => {
      const user = await activeClient.me(session.access_token);
      setAccessToken(session.access_token);
      setPrincipal(user);
      setStatus("authenticated");
    },
    [activeClient]
  );
  useEffect(() => {
    let mounted = true;
    activeClient
      .refresh()
      .then(async session => {
        if (mounted) await applySession(session);
      })
      .catch(() => {
        if (mounted) {
          setAccessToken(null);
          setPrincipal(null);
          setStatus("anonymous");
        }
      });
    return () => {
      mounted = false;
    };
  }, [activeClient, applySession]);
  const login = useCallback(
    async (username: string, password: string) =>
      applySession(await activeClient.login(username, password)),
    [activeClient, applySession]
  );
  const logout = useCallback(async () => {
    await activeClient.logout();
    setAccessToken(null);
    setPrincipal(null);
    setStatus("anonymous");
  }, [activeClient]);
  const authorizedFetch = useCallback(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      try {
        return await activeClient.authorizedFetch(input, init);
      } catch (error) {
        setAccessToken(null);
        setPrincipal(null);
        setStatus("anonymous");
        throw error;
      }
    },
    [activeClient]
  );
  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      accessToken,
      principal,
      login,
      logout,
      authorizedFetch,
      hasRole: (...roles) =>
        Boolean(
          principal && roles.some(role => principal.roles.includes(role))
        ),
    }),
    [accessToken, authorizedFetch, login, logout, principal, status]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth(): AuthContextValue {
  return useContext(AuthContext);
}
