"use client";

import Link from "next/link";
import {
  ArrowRight,
  CheckCircle,
  CloudArrowUp,
  FileText,
  ShieldCheck,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/features/auth/AuthProvider";
import { toErrorMessage } from "@/lib/error-message";

import {
  getKnowledgeIngestion,
  type KnowledgeIngestion,
  uploadKnowledgeDocument,
} from "./knowledge-api";

const DOMAIN_ID = "agriculture";
const ACCEPTED_EXTENSIONS = [".txt", ".csv"];
const POLLABLE_STATUSES = new Set(["queued", "running", "retrying"]);

function isSupportedFile(file: File | null): boolean {
  if (!file) return false;
  return ACCEPTED_EXTENSIONS.some(extension =>
    file.name.toLowerCase().endsWith(extension)
  );
}

function statusCopy(status: string): string {
  const labels: Record<string, string> = {
    queued: "Đang chờ worker index",
    running: "Worker đang phân tích và index",
    retrying: "Đang thử index lại",
    completed: "Đã sẵn sàng cho AI Copilot",
    dead_letter: "Index chưa hoàn tất",
  };
  return labels[status] ?? "Đang cập nhật trạng thái index";
}

function StatusMark({ status }: { status: string }) {
  if (status === "completed") {
    return <CheckCircle size={18} weight="fill" className="text-[#28765a]" />;
  }
  if (status === "dead_letter") {
    return <WarningCircle size={18} weight="fill" className="text-[#9a7128]" />;
  }
  return <SpinnerGap size={18} className="animate-spin text-[#28765a]" />;
}

export function KnowledgeBaseWorkspace() {
  const { hasRole, authorizedFetch, status: authStatus } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<KnowledgeIngestion | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canIngest = hasRole("admin", "expert");
  const fileIsSupported = isSupportedFile(file);
  const isPolling = Boolean(job && POLLABLE_STATUSES.has(job.status));

  const helperText = useMemo(() => {
    if (!file)
      return "Hỗ trợ TXT và CSV. Dữ liệu được index riêng theo domain.";
    return fileIsSupported
      ? `${file.name} đã sẵn sàng để gửi.`
      : "Chỉ nhận tệp TXT hoặc CSV trong phiên bản hiện tại.";
  }, [file, fileIsSupported]);

  useEffect(() => {
    if (!job || !POLLABLE_STATUSES.has(job.status)) return;
    const timer = window.setInterval(() => {
      void getKnowledgeIngestion(authorizedFetch, job.job_id)
        .then(setJob)
        .catch(() => undefined);
    }, 3000);
    return () => window.clearInterval(timer);
  }, [authorizedFetch, job]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || !fileIsSupported || !canIngest || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      setJob(
        await uploadKnowledgeDocument(authorizedFetch, {
          file,
          domainId: DOMAIN_ID,
        })
      );
    } catch (uploadError) {
      setError(toErrorMessage(uploadError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-[100dvh] bg-[#f4f7f4] px-3 py-3 text-[#18201b] sm:px-5 sm:py-5 lg:px-7 lg:py-7">
      <div className="mx-auto max-w-[1400px]">
        <header className="flex flex-col gap-5 rounded-3xl border border-black/[0.08] bg-[#18201b] px-5 py-5 text-[#eaf2ec] shadow-[0_16px_36px_rgba(24,32,27,0.08)] sm:px-7 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#28765a]">
              <CloudArrowUp size={22} weight="fill" />
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight">Canopy</p>
              <p className="text-xs text-white/55">AI-native workspace</p>
            </div>
          </div>
          <nav
            className="flex flex-wrap gap-2 text-sm"
            aria-label="Điều hướng AI workspace"
          >
            <Link
              className="rounded-xl px-3 py-2 text-white/70 transition hover:bg-white/[0.08] hover:text-white"
              href="/ai-copilot"
            >
              AI Copilot
            </Link>
            <Link
              className="rounded-xl bg-white/10 px-3 py-2 font-medium text-white"
              href="/knowledge"
              aria-current="page"
            >
              Knowledge Base
            </Link>
            <Link
              className="rounded-xl px-3 py-2 text-white/70 transition hover:bg-white/[0.08] hover:text-white"
              href="/ai-operations"
            >
              AI Operations
            </Link>
          </nav>
        </header>

        <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_330px]">
          <section className="rounded-3xl border border-black/[0.08] bg-[#fbfcfa] p-5 shadow-[0_16px_36px_rgba(24,32,27,0.045)] sm:p-8">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#28765a]">
              Knowledge Base
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.045em] text-[#18201b] sm:text-4xl">
              Nạp tri thức để Copilot có bằng chứng.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-[#637068] sm:text-base">
              Tài liệu được đưa vào hàng đợi, index theo domain và chỉ được dùng
              khi hoàn tất kiểm chứng.
            </p>

            {authStatus === "loading" ? (
              <div className="mt-9 flex items-center gap-3 rounded-2xl border border-black/[0.08] bg-white px-4 py-4 text-sm text-[#526057]">
                <SpinnerGap size={18} className="animate-spin text-[#28765a]" />
                Đang kiểm tra quyền nạp tri thức…
              </div>
            ) : canIngest ? (
              <form onSubmit={submit} className="mt-9">
                <div className="rounded-3xl border border-dashed border-[#28765a]/35 bg-[#f4f8f4] p-5 sm:p-7">
                  <label
                    htmlFor="knowledge-file"
                    className="block text-sm font-semibold text-[#18201b]"
                  >
                    Tệp tri thức
                  </label>
                  <p className="mt-1 text-xs leading-5 text-[#637068]">
                    {helperText}
                  </p>
                  <input
                    id="knowledge-file"
                    type="file"
                    accept=".txt,.csv,text/plain,text/csv"
                    onChange={event => {
                      setFile(event.target.files?.[0] ?? null);
                      setError(null);
                    }}
                    className="mt-5 block w-full cursor-pointer rounded-xl border border-black/[0.09] bg-white px-3 py-3 text-sm text-[#526057] file:mr-4 file:rounded-lg file:border-0 file:bg-[#e7f2ea] file:px-3 file:py-2 file:text-xs file:font-semibold file:text-[#28765a]"
                  />
                  <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-[#28765a]/12 pt-5">
                    <span className="inline-flex items-center gap-2 text-xs text-[#637068]">
                      <ShieldCheck
                        size={16}
                        weight="fill"
                        className="text-[#28765a]"
                      />
                      Domain: Nông nghiệp
                    </span>
                    <button
                      type="submit"
                      disabled={!fileIsSupported || submitting}
                      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#28765a] px-4 py-2.5 text-sm font-semibold text-white transition duration-300 hover:bg-[#205f48] active:translate-y-px disabled:cursor-not-allowed disabled:bg-[#a4b6a8]"
                    >
                      {submitting ? (
                        <SpinnerGap size={17} className="animate-spin" />
                      ) : (
                        <CloudArrowUp size={17} weight="bold" />
                      )}
                      Bắt đầu index
                    </button>
                  </div>
                </div>
                {error ? (
                  <p
                    role="alert"
                    className="mt-3 rounded-xl border border-[#d7b571]/50 bg-[#fffaf0] px-4 py-3 text-sm text-[#765d2e]"
                  >
                    {error}
                  </p>
                ) : null}
              </form>
            ) : (
              <section
                className="mt-9 rounded-3xl border border-[#d7b571]/50 bg-[#fffaf0] p-5 sm:p-6"
                aria-label="Quyền nạp tri thức"
              >
                <div className="flex gap-3">
                  <ShieldCheck
                    size={21}
                    weight="fill"
                    className="mt-0.5 shrink-0 text-[#9a7128]"
                  />
                  <div>
                    <p className="font-semibold text-[#5d4518]">
                      Chỉ chuyên gia hoặc quản trị viên mới có thể nạp tri thức.
                    </p>
                    <p className="mt-2 text-sm leading-6 text-[#765d2e]">
                      Hãy đăng nhập bằng vai trò phù hợp để bảo vệ nguồn chuyên
                      môn của domain.
                    </p>
                    <Link
                      href="/ai-copilot"
                      className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-[#765d2e] underline underline-offset-4"
                    >
                      Quay lại AI Copilot <ArrowRight size={15} />
                    </Link>
                  </div>
                </div>
              </section>
            )}
          </section>

          <aside className="rounded-3xl border border-black/[0.08] bg-white p-5 shadow-[0_16px_36px_rgba(24,32,27,0.035)] sm:p-6">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#78837b]">
              Index status
            </p>
            {job ? (
              <section className="mt-5" aria-live="polite">
                <div className="flex items-start gap-3">
                  <StatusMark status={job.status} />
                  <div>
                    <p className="text-sm font-semibold text-[#18201b]">
                      {statusCopy(job.status)}
                    </p>
                    <p className="mt-1 font-mono text-xs text-[#78837b]">
                      job {job.job_id.slice(0, 8)}
                    </p>
                  </div>
                </div>
                <p className="mt-5 text-sm leading-6 text-[#637068]">
                  {isPolling
                    ? "Trạng thái sẽ tự cập nhật khi worker xử lý tài liệu."
                    : job.status === "completed"
                      ? "Bạn có thể quay về Copilot để truy vấn nguồn vừa được index."
                      : "Worker đã dừng xử lý. Hãy kiểm tra lại nội dung tệp và thử nạp lại."}
                </p>
                {job.last_error ? (
                  <p className="mt-3 text-xs text-[#9a7128]">
                    Mã lỗi: {job.last_error}
                  </p>
                ) : null}
                <Link
                  href={`/knowledge/${job.job_id}`}
                  className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#28765a] underline underline-offset-4"
                >
                  Xem chi tiết job <ArrowRight size={15} />
                </Link>
                {job.status === "completed" ? (
                  <Link
                    href="/ai-copilot"
                    className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-[#28765a] underline underline-offset-4"
                  >
                    Mở AI Copilot <ArrowRight size={15} />
                  </Link>
                ) : null}
              </section>
            ) : (
              <section className="mt-5 rounded-2xl border border-dashed border-black/[0.12] p-5 text-center">
                <FileText size={28} className="mx-auto text-[#96a198]" />
                <p className="mt-3 text-sm font-medium text-[#526057]">
                  Chưa có lượt nạp trong phiên này
                </p>
                <p className="mt-2 text-xs leading-5 text-[#78837b]">
                  Sau khi gửi tệp, trạng thái index và đường dẫn theo dõi sẽ
                  xuất hiện tại đây.
                </p>
              </section>
            )}
            <div className="mt-7 border-t border-black/[0.07] pt-5">
              <p className="text-xs font-semibold text-[#18201b]">
                Nguyên tắc an toàn
              </p>
              <p className="mt-2 text-xs leading-5 text-[#637068]">
                Memory hỗ trợ ngữ cảnh hội thoại; tài liệu đã index mới là bằng
                chứng để Copilot kết luận.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
