"use client";

import { LockKey, SpinnerGap } from "@phosphor-icons/react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/features/auth/AuthProvider";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!username.trim() || !password) return;
    setLoading(true);
    setError(null);
    try {
      await login(username.trim(), password);
      router.replace("/ai-copilot");
    } catch {
      setError("Không thể đăng nhập. Vui lòng kiểm tra thông tin và thử lại.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <main className="grid min-h-[100dvh] place-items-center bg-[#f4f7f4] p-5 text-[#18201b]">
      <form
        onSubmit={submit}
        className="w-full max-w-md rounded-3xl border border-black/[0.08] bg-white p-7 shadow-[0_18px_50px_rgba(24,32,27,0.08)] sm:p-9"
      >
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#e7f2ea] text-[#28765a]">
          <LockKey size={22} weight="fill" />
        </span>
        <h1 className="mt-6 text-2xl font-semibold tracking-[-0.04em]">
          Đăng nhập không gian làm việc
        </h1>
        <p className="mt-2 text-sm leading-6 text-[#637068]">
          Phiên truy cập được bảo vệ bằng refresh cookie HttpOnly và phân quyền
          ở backend.
        </p>
        <label className="mt-7 block text-sm font-medium" htmlFor="username">
          Tên đăng nhập
        </label>
        <input
          id="username"
          autoComplete="username"
          value={username}
          onChange={event => setUsername(event.target.value)}
          className="mt-2 w-full rounded-xl border border-black/[0.12] px-3 py-3 text-sm outline-none transition focus:border-[#28765a]"
          required
        />
        <label className="mt-4 block text-sm font-medium" htmlFor="password">
          Mật khẩu
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={event => setPassword(event.target.value)}
          className="mt-2 w-full rounded-xl border border-black/[0.12] px-3 py-3 text-sm outline-none transition focus:border-[#28765a]"
          required
        />
        {error ? (
          <p
            role="alert"
            className="mt-4 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-800"
          >
            {error}
          </p>
        ) : null}
        <button
          type="submit"
          disabled={loading || !username.trim() || !password}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-[#28765a] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#1d6147] disabled:cursor-not-allowed disabled:bg-[#b6c1b9]"
        >
          {loading ? <SpinnerGap className="animate-spin" size={18} /> : null}
          Đăng nhập
        </button>
      </form>
    </main>
  );
}
