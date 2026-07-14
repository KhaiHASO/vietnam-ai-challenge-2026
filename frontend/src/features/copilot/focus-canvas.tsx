"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowClockwise,
  BookOpenText,
  CaretDown,
  CheckCircle,
  Copy,
  FileText,
  ShieldCheck,
  Sparkle,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { FormEvent, useMemo, useState, useSyncExternalStore } from "react";

import type { CopilotCitation } from "./copilot.types";
import { MagneticSendButton } from "./magnetic-send-button";
import { useCopilotStream } from "./use-copilot-stream";
import { useAuth } from "@/features/auth/AuthProvider";

const DOMAIN_OPTIONS = [
  { id: "agriculture", label: "Nông nghiệp", detail: "VietGAP & canh tác" },
  { id: "education", label: "Giáo dục", detail: "Quy chế & học vụ" },
  { id: "sme", label: "Vận hành SME", detail: "Chính sách & quy trình" },
];

const ACTIVE_DOMAIN_OPTIONS = DOMAIN_OPTIONS.filter(
  item => item.id === "agriculture"
);

const SUGGESTIONS = [
  "Thời gian cách ly sau khi phun thuốc theo VietGAP là bao lâu?",
  "Tóm tắt các điều kiện cần kiểm tra trước khi xử lý bệnh đạo ôn.",
  "Nguồn tài liệu nào hỗ trợ khuyến nghị này?",
];

function PhaseLabel({ phase }: { phase: string }) {
  const labels: Record<string, string> = {
    connecting: "Đang kết nối",
    retrieving: "Đang đối chiếu nguồn",
    streaming: "Đang trả lời",
    completed: "Đã kiểm chứng",
    abstained: "Cần thêm bằng chứng",
    approval: "Chờ phê duyệt",
    degraded: "Chế độ dự phòng",
    error: "Không thể hoàn tất",
    idle: "Sẵn sàng",
  };
  return <span>{labels[phase] ?? "Sẵn sàng"}</span>;
}

function CitationCard({
  citation,
  index,
}: {
  citation: CopilotCitation;
  index: number;
}) {
  return (
    <article className="rounded-2xl border border-black/[0.08] bg-white p-4 shadow-[0_8px_24px_rgba(24,32,27,0.035)]">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[#e8f2eb] text-sm font-semibold text-[#28765a]">
          {index + 1}
        </span>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-[#18201b]">
            {citation.label ?? citation.document_id}
          </p>
          <p className="mt-1 line-clamp-3 text-xs leading-5 text-[#637068]">
            {citation.quote ?? "Đã liên kết với câu trả lời hiện tại."}
          </p>
          {citation.url ? (
            <a
              className="mt-3 inline-flex text-xs font-semibold text-[#28765a] underline underline-offset-4"
              href={citation.url}
            >
              Mở tài liệu
            </a>
          ) : null}
        </div>
      </div>
    </article>
  );
}

function subscribeToSessionId() {
  return () => undefined;
}

function getSessionIdSnapshot() {
  const savedSession =
    window.localStorage.getItem("ai_copilot_session") ?? crypto.randomUUID();
  window.localStorage.setItem("ai_copilot_session", savedSession);
  return savedSession;
}

export function FocusCanvas() {
  const { state, send, reset } = useCopilotStream();
  const { accessToken } = useAuth();
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("agriculture");
  const sessionId = useSyncExternalStore(
    subscribeToSessionId,
    getSessionIdSnapshot,
    () => ""
  );
  const [copied, setCopied] = useState(false);

  const isBusy = ["connecting", "retrieving", "streaming"].includes(
    state.phase
  );
  const evidence = state.citations;
  const activeDomain = useMemo(
    () =>
      ACTIVE_DOMAIN_OPTIONS.find(item => item.id === domain) ??
      ACTIVE_DOMAIN_OPTIONS[0],
    [domain]
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanQuery = query.trim();
    if (!cleanQuery || isBusy) return;
    if (!accessToken || !sessionId) {
      reset();
      return;
    }
    setQuery("");
    await send({
      sessionId,
      accessToken,
      idempotencyKey: crypto.randomUUID(),
      expectedRevision: state.conversationRevision,
      query: cleanQuery,
      domainId: domain,
    });
  }

  async function copyAnswer() {
    if (!state.draft) return;
    await navigator.clipboard?.writeText(state.draft);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  const accessNeeded = !accessToken && state.phase === "idle";
  return (
    <main className="min-h-[100dvh] bg-[#f4f7f4] px-3 py-3 text-[#18201b] sm:px-5 sm:py-5 lg:px-7 lg:py-7">
      <div className="mx-auto grid max-w-[1560px] gap-3 lg:grid-cols-[220px_minmax(0,1fr)_310px]">
        <aside className="rounded-3xl border border-black/[0.08] bg-[#18201b] p-5 text-[#eaf2ec] lg:min-h-[calc(100dvh-56px)]">
          <div className="flex items-center gap-3 border-b border-white/10 pb-5">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#28765a] text-white">
              <Sparkle size={20} weight="fill" />
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight">Canopy</p>
              <p className="text-xs text-white/55">AI-native workspace</p>
            </div>
          </div>
          <nav className="mt-7" aria-label="Lĩnh vực hoạt động">
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-white/45">
              Domain pack
            </p>
            <div className="flex gap-2 overflow-x-auto lg:block lg:space-y-2">
              {ACTIVE_DOMAIN_OPTIONS.map(item => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setDomain(item.id)}
                  aria-pressed={domain === item.id}
                  className={`min-w-[150px] rounded-2xl px-3 py-3 text-left transition-colors lg:min-w-0 ${domain === item.id ? "bg-white/10 text-white" : "text-white/65 hover:bg-white/[0.06] hover:text-white"}`}
                >
                  <span className="block text-sm font-medium">
                    {item.label}
                  </span>
                  <span className="mt-1 block text-xs text-inherit opacity-65">
                    {item.detail}
                  </span>
                </button>
              ))}
            </div>
          </nav>
          <div className="mt-7 hidden border-t border-white/10 pt-5 lg:block">
            <p className="text-xs leading-5 text-white/55">
              Mỗi câu trả lời đều gắn với domain pack, phiên bản chỉ mục và
              policy hiện hành.
            </p>
          </div>
          <div className="mt-auto hidden lg:flex lg:items-center lg:gap-2 lg:pt-8">
            <span className="h-2 w-2 rounded-full bg-[#69c68e]" />
            <span className="text-xs text-white/55">
              Assurance pipeline active
            </span>
          </div>
        </aside>

        <section className="flex min-h-[calc(100dvh-56px)] flex-col overflow-hidden rounded-3xl border border-black/[0.08] bg-[#fbfcfa]">
          <header className="flex flex-wrap items-center justify-between gap-4 border-b border-black/[0.07] px-5 py-4 sm:px-7">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-semibold tracking-[-0.03em]">
                  AI Copilot
                </h1>
                <span className="rounded-full bg-[#e7f2ea] px-2.5 py-1 text-[11px] font-semibold text-[#28765a]">
                  {activeDomain.label}
                </span>
              </div>
              <p className="mt-1 text-sm text-[#637068]">
                Đặt câu hỏi, đối chiếu nguồn, rồi mới đưa ra kết luận.
              </p>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-black/[0.08] bg-white px-3 py-2 text-xs font-medium text-[#526057]">
              <span
                className={`h-2 w-2 rounded-full ${isBusy ? "bg-[#b88735]" : "bg-[#4aab70]"}`}
              />
              <PhaseLabel phase={state.phase} />
              <CaretDown size={13} aria-hidden="true" />
            </div>
          </header>

          <div className="flex flex-1 flex-col px-5 py-7 sm:px-7 sm:py-9">
            <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center">
              {!state.draft &&
              state.phase !== "abstained" &&
              state.phase !== "error" ? (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35 }}
                  className="max-w-xl"
                >
                  <p className="text-sm font-semibold text-[#28765a]">
                    TRUY VẤN CÓ KIỂM CHỨNG
                  </p>
                  <h2 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-[#18201b] sm:text-4xl">
                    Một không gian tập trung cho câu trả lời có trách nhiệm.
                  </h2>
                  <p className="mt-5 max-w-lg text-base leading-7 text-[#637068]">
                    Copilot tách ký ức hội thoại khỏi bằng chứng chuyên môn, xác
                    thực citation trước khi trả lời và chủ động từ chối khi
                    nguồn chưa đủ.
                  </p>
                </motion.div>
              ) : null}

              {isBusy ? (
                <div className="mt-8 flex items-center gap-3 text-sm text-[#526057]">
                  <SpinnerGap
                    className="animate-spin text-[#28765a]"
                    size={20}
                  />
                  <span>
                    {state.phase === "retrieving"
                      ? "Đang tra cứu và kiểm tra phạm vi nguồn…"
                      : "Đang chuẩn bị phản hồi…"}
                  </span>
                </div>
              ) : null}
              {state.draft ? (
                <motion.article
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className="mt-8 rounded-3xl border border-black/[0.08] bg-white p-5 sm:p-7"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2 text-sm font-semibold">
                      <CheckCircle
                        className="text-[#28765a]"
                        weight="fill"
                        size={18}
                      />{" "}
                      Phản hồi đã hoàn tất
                    </div>
                    <button
                      type="button"
                      onClick={copyAnswer}
                      aria-label="Sao chép câu trả lời"
                      className="rounded-xl p-2 text-[#526057] transition-colors hover:bg-[#edf3ee] hover:text-[#28765a]"
                    >
                      <Copy size={18} />
                    </button>
                  </div>
                  <p className="mt-5 whitespace-pre-wrap text-[15px] leading-7 text-[#29322c]">
                    {state.draft}
                  </p>
                  {copied ? (
                    <p className="mt-3 text-xs font-medium text-[#28765a]">
                      Đã sao chép phản hồi.
                    </p>
                  ) : null}
                </motion.article>
              ) : null}
              {state.phase === "abstained" && state.abstention ? (
                <article className="mt-8 rounded-3xl border border-[#d7b571]/50 bg-[#fffaf0] p-5 sm:p-7">
                  <div className="flex gap-3">
                    <WarningCircle
                      className="mt-0.5 shrink-0 text-[#9a7128]"
                      size={21}
                      weight="fill"
                    />
                    <div>
                      <p className="font-semibold text-[#5d4518]">
                        Chưa thể kết luận một cách an toàn
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[#765d2e]">
                        {state.abstention.user_message}
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        {state.abstention.recovery_actions.map(action => (
                          <span
                            key={action}
                            className="rounded-full border border-[#d7b571]/60 px-2.5 py-1 text-xs text-[#765d2e]"
                          >
                            {action.replaceAll("_", " ")}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </article>
              ) : null}
              {state.phase === "approval" && state.approval ? (
                <article className="mt-8 rounded-3xl border border-[#28765a]/25 bg-[#eef7f0] p-5 sm:p-7">
                  <div className="flex gap-3">
                    <ShieldCheck
                      className="mt-0.5 shrink-0 text-[#28765a]"
                      size={21}
                      weight="fill"
                    />
                    <div>
                      <p className="font-semibold text-[#1d513d]">
                        Cần phê duyệt trước khi thực hiện
                      </p>
                      <p className="mt-2 text-sm leading-6 text-[#426d58]">
                        Hệ thống đã giữ lại hành động có rủi ro để chuyên gia
                        kiểm tra. Copilot không tự thực thi thay bạn.
                      </p>
                      {state.approval.action_type ? (
                        <p className="mt-4 font-mono text-xs text-[#28765a]">
                          action: {state.approval.action_type}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </article>
              ) : null}
              {state.phase === "degraded" ? (
                <article className="mt-5 border-l-2 border-[#b88735] pl-4 text-sm leading-6 text-[#765d2e]">
                  Phản hồi này dùng tuyến dự phòng. Hãy kiểm tra kỹ nguồn bằng
                  chứng trước khi áp dụng khuyến nghị.
                </article>
              ) : null}
              {state.phase === "error" ? (
                <article className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
                  <strong>Không thể hoàn tất yêu cầu.</strong> {state.error}
                </article>
              ) : null}
              {accessNeeded ? (
                <p className="mt-8 text-sm text-[#637068]">
                  Trả lời chỉ được đưa ra khi có bằng chứng phù hợp.
                </p>
              ) : null}
            </div>

            <div className="mx-auto mt-8 w-full max-w-3xl">
              <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
                {SUGGESTIONS.map(suggestion => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setQuery(suggestion)}
                    className="shrink-0 rounded-full border border-black/[0.08] bg-white px-3 py-1.5 text-xs text-[#526057] transition-colors hover:border-[#28765a]/40 hover:text-[#28765a]"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
              <form
                onSubmit={submit}
                className="rounded-2xl border border-black/[0.12] bg-white p-2 shadow-[0_12px_30px_rgba(24,32,27,0.06)]"
              >
                <label className="sr-only" htmlFor="copilot-question">
                  Câu hỏi cho AI Copilot
                </label>
                <div className="flex items-end gap-2">
                  <textarea
                    id="copilot-question"
                    value={query}
                    onChange={event => setQuery(event.target.value)}
                    rows={2}
                    placeholder="Hỏi về chính sách, quy trình hoặc dữ liệu chuyên môn…"
                    className="min-h-14 flex-1 resize-none border-0 bg-transparent px-3 py-2 text-sm leading-6 outline-none placeholder:text-[#96a198]"
                  />
                  <MagneticSendButton
                    disabled={!query.trim() || isBusy || !accessToken}
                  />
                </div>
                <div className="flex items-center justify-between px-3 pb-1 pt-2 text-[11px] text-[#78837b]">
                  <span>
                    <ShieldCheck
                      className="mr-1 inline text-[#28765a]"
                      size={14}
                      weight="fill"
                    />{" "}
                    Không dùng memory làm bằng chứng
                  </span>
                  <span>
                    {accessToken ? "Đã xác thực" : "Cần đăng nhập để gửi"}
                  </span>
                </div>
              </form>
            </div>
          </div>
        </section>

        <aside className="rounded-3xl border border-black/[0.08] bg-[#fbfcfa] p-5 lg:min-h-[calc(100dvh-56px)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold">Nguồn bằng chứng</p>
              <p className="mt-1 text-xs text-[#637068]">
                Dùng để kiểm chứng phản hồi
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/knowledge"
                className="text-xs font-semibold text-[#28765a] underline underline-offset-4"
              >
                Nạp tri thức
              </Link>
              <Link
                href="/ai-operations"
                className="text-xs font-semibold text-[#526057] underline underline-offset-4"
              >
                AI Operations
              </Link>
              <BookOpenText className="text-[#28765a]" size={22} />
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {evidence.length ? (
              evidence.map((citation, index) => (
                <CitationCard
                  key={`${citation.document_id}-${index}`}
                  citation={citation}
                  index={index}
                />
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-black/[0.12] px-4 py-8 text-center">
                <FileText className="mx-auto text-[#96a198]" size={27} />
                <p className="mt-3 text-sm font-medium text-[#526057]">
                  Chưa có nguồn cho lượt này
                </p>
                <p className="mt-1 text-xs leading-5 text-[#78837b]">
                  Khi truy vấn hoàn tất, citation được xác thực sẽ xuất hiện ở
                  đây.
                </p>
              </div>
            )}
          </div>
          <div className="mt-6 border-t border-black/[0.07] pt-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[#78837b]">
              Assurance
            </p>
            <ul className="mt-3 space-y-3 text-xs text-[#526057]">
              <li className="flex gap-2">
                <ShieldCheck
                  className="shrink-0 text-[#28765a]"
                  size={16}
                  weight="fill"
                />{" "}
                Scope và policy được kiểm tra trước khi trả lời
              </li>
              <li className="flex gap-2">
                <CheckCircle
                  className="shrink-0 text-[#28765a]"
                  size={16}
                  weight="fill"
                />{" "}
                Citation phải cùng tenant, domain, index revision
              </li>
            </ul>
          </div>
          <button
            type="button"
            onClick={reset}
            className="mt-6 inline-flex items-center gap-2 text-xs font-semibold text-[#526057] hover:text-[#28765a]"
          >
            <ArrowClockwise size={15} /> Phiên phản hồi mới
          </button>
        </aside>
      </div>
    </main>
  );
}
