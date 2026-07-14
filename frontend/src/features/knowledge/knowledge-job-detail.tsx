"use client";

import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  ArrowClockwise,
  CheckCircle,
  ShieldCheck,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/features/auth/AuthProvider";
import { toErrorMessage } from "@/lib/error-message";

import {
  getKnowledgeIngestion,
  type KnowledgeIngestion,
} from "./knowledge-api";

function jobTitle(status: string): string {
  return (
    {
      queued: "Đang chờ worker index",
      running: "Worker đang phân tích và index",
      retrying: "Đang thử index lại",
      completed: "Đã sẵn sàng cho AI Copilot",
      dead_letter: "Index chưa hoàn tất",
    }[status] ?? "Đang cập nhật trạng thái index"
  );
}

export function KnowledgeJobDetail({ jobId }: { jobId: string }) {
  const { authorizedFetch } = useAuth();
  const [job, setJob] = useState<KnowledgeIngestion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setJob(await getKnowledgeIngestion(authorizedFetch, jobId));
    } catch (requestError) {
      setError(toErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [authorizedFetch, jobId]);

  useEffect(() => {
    let mounted = true;
    async function loadInitialStatus() {
      try {
        const nextJob = await getKnowledgeIngestion(authorizedFetch, jobId);
        if (mounted) setJob(nextJob);
      } catch (requestError) {
        if (mounted) setError(toErrorMessage(requestError));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    void loadInitialStatus();
    return () => {
      mounted = false;
    };
  }, [authorizedFetch, jobId]);

  return (
    <main className="min-h-[100dvh] bg-[#f4f7f4] px-3 py-3 text-[#18201b] sm:px-5 sm:py-5 lg:px-7 lg:py-7">
      <section className="mx-auto max-w-4xl rounded-3xl border border-black/[0.08] bg-[#fbfcfa] p-5 shadow-[0_16px_36px_rgba(24,32,27,0.045)] sm:p-8">
        <Link
          href="/knowledge"
          className="inline-flex items-center gap-2 text-sm font-semibold text-[#526057] transition hover:text-[#28765a]"
        >
          <ArrowLeft size={16} /> Knowledge Base
        </Link>
        <div className="mt-9 flex flex-col gap-6 border-b border-black/[0.07] pb-7 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#28765a]">
              Ingestion job
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.045em]">
              Theo dõi quá trình index
            </h1>
            <p className="mt-3 font-mono text-sm text-[#637068]">{jobId}</p>
          </div>
          <button
            type="button"
            onClick={() => void refresh()}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-black/[0.1] bg-white px-4 py-2.5 text-sm font-semibold text-[#526057] transition hover:border-[#28765a]/35 hover:text-[#28765a] disabled:opacity-60"
          >
            <ArrowClockwise
              size={17}
              className={loading ? "animate-spin" : undefined}
            />{" "}
            Cập nhật
          </button>
        </div>

        {loading && !job ? (
          <div className="mt-8 flex items-center gap-3 text-sm text-[#526057]">
            <SpinnerGap size={19} className="animate-spin text-[#28765a]" />{" "}
            Đang đọc trạng thái index…
          </div>
        ) : null}
        {error ? (
          <section
            role="alert"
            className="mt-8 rounded-2xl border border-[#d7b571]/50 bg-[#fffaf0] p-5 text-sm leading-6 text-[#765d2e]"
          >
            <WarningCircle
              size={19}
              weight="fill"
              className="mr-2 inline text-[#9a7128]"
            />{" "}
            {error}
          </section>
        ) : null}
        {job ? (
          <section
            className="mt-8 rounded-3xl border border-black/[0.08] bg-white p-5 sm:p-6"
            aria-live="polite"
          >
            <div className="flex items-start gap-3">
              {job.status === "completed" ? (
                <CheckCircle
                  size={23}
                  weight="fill"
                  className="mt-0.5 text-[#28765a]"
                />
              ) : job.status === "dead_letter" ? (
                <WarningCircle
                  size={23}
                  weight="fill"
                  className="mt-0.5 text-[#9a7128]"
                />
              ) : (
                <SpinnerGap
                  size={23}
                  className="mt-0.5 animate-spin text-[#28765a]"
                />
              )}
              <div>
                <p className="font-semibold text-[#18201b]">
                  {jobTitle(job.status)}
                </p>
                <p className="mt-2 text-sm leading-6 text-[#637068]">
                  {job.status === "completed"
                    ? "Nguồn đã đi qua pipeline ingestion và sẵn sàng phục vụ truy vấn có kiểm chứng."
                    : "Trạng thái này được lấy trực tiếp từ hàng đợi ingestion của tenant hiện tại."}
                </p>
              </div>
            </div>
            <dl className="mt-6 grid gap-4 border-t border-black/[0.07] pt-5 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-[#78837b]">
                  Trạng thái
                </dt>
                <dd className="mt-2 text-sm font-medium text-[#18201b]">
                  {job.status}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-[#78837b]">
                  Số lần thử
                </dt>
                <dd className="mt-2 text-sm font-medium text-[#18201b]">
                  {job.attempts}
                </dd>
              </div>
            </dl>
            {job.last_error ? (
              <p className="mt-5 text-sm text-[#9a7128]">
                Mã lỗi an toàn: {job.last_error}
              </p>
            ) : null}
            {job.status === "completed" ? (
              <Link
                href="/ai-copilot"
                className="mt-7 inline-flex items-center gap-2 rounded-xl bg-[#28765a] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#205f48] active:translate-y-px"
              >
                Mở AI Copilot <ArrowRight size={17} />
              </Link>
            ) : null}
          </section>
        ) : null}
        <aside className="mt-8 flex gap-3 rounded-2xl border border-[#28765a]/15 bg-[#eef7f0] p-4 text-sm leading-6 text-[#426d58]">
          <ShieldCheck
            size={19}
            weight="fill"
            className="mt-0.5 shrink-0 text-[#28765a]"
          />
          Job chỉ hiển thị khi cùng tenant với tài khoản hiện tại. Đường dẫn lưu
          trữ và payload nội bộ không xuất hiện trên màn hình này.
        </aside>
      </section>
    </main>
  );
}
