import Link from "next/link";
import {
  ArrowRight,
  BookOpenText,
  Database,
  ShieldCheck,
  WarningCircle,
} from "@phosphor-icons/react";

const CONTROLS = [
  {
    icon: ShieldCheck,
    title: "Assurance trước khi trả lời",
    detail:
      "Kiểm tra scope, policy, claim và citation trước khi Copilot kết luận.",
  },
  {
    icon: Database,
    title: "Memory không phải bằng chứng chuyên môn",
    detail:
      "Ký ức chỉ giữ ngữ cảnh hội thoại; retrieval từ Knowledge Base mới cung cấp nguồn để kiểm chứng.",
  },
  {
    icon: WarningCircle,
    title: "Typed abstention thay cho trả lời bừa",
    detail:
      "Khi nguồn không đủ hoặc policy chặn, hệ thống trả về lý do và hành động phục hồi rõ ràng.",
  },
];

export function AiOperationsWorkspace() {
  return (
    <main className="min-h-[100dvh] bg-[#f4f7f4] px-3 py-3 text-[#18201b] sm:px-5 sm:py-5 lg:px-7 lg:py-7">
      <div className="mx-auto max-w-[1400px]">
        <header className="flex flex-col gap-5 rounded-3xl border border-black/[0.08] bg-[#18201b] px-5 py-5 text-[#eaf2ec] shadow-[0_16px_36px_rgba(24,32,27,0.08)] sm:px-7 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#28765a]">
              <ShieldCheck size={22} weight="fill" />
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
              className="rounded-xl px-3 py-2 text-white/70 transition hover:bg-white/[0.08] hover:text-white"
              href="/knowledge"
            >
              Knowledge Base
            </Link>
            <Link
              className="rounded-xl bg-white/10 px-3 py-2 font-medium text-white"
              href="/ai-operations"
              aria-current="page"
            >
              AI Operations
            </Link>
          </nav>
        </header>

        <section className="mt-5 rounded-3xl border border-black/[0.08] bg-[#fbfcfa] p-5 shadow-[0_16px_36px_rgba(24,32,27,0.045)] sm:p-8">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#28765a]">
              Assurance surface
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.045em] sm:text-4xl">
              AI Operations
            </h1>
            <p className="mt-4 text-sm leading-6 text-[#637068] sm:text-base">
              Một lớp quan sát dành cho demo: giải thích các guardrail đang bảo
              vệ câu trả lời, tách khỏi trải nghiệm hỏi đáp hằng ngày.
            </p>
          </div>

          <div className="mt-9 grid gap-px overflow-hidden rounded-2xl border border-black/[0.08] bg-black/[0.08] lg:grid-cols-[1.2fr_0.8fr]">
            <section className="bg-white p-5 sm:p-6">
              <p className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#78837b]">
                Controls đã cấu hình
              </p>
              <div className="mt-5 space-y-5">
                {CONTROLS.map(control => {
                  const Icon = control.icon;
                  return (
                    <article key={control.title} className="flex gap-3">
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#e7f2ea] text-[#28765a]">
                        <Icon size={18} weight="fill" />
                      </span>
                      <div>
                        <h2 className="text-sm font-semibold text-[#18201b]">
                          {control.title}
                        </h2>
                        <p className="mt-1 text-sm leading-6 text-[#637068]">
                          {control.detail}
                        </p>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
            <aside className="bg-[#f7faf7] p-5 sm:p-6">
              <BookOpenText size={26} className="text-[#28765a]" />
              <p className="mt-4 text-sm font-semibold text-[#18201b]">
                Không có số liệu vận hành trực tiếp trong phiên này.
              </p>
              <p className="mt-2 text-sm leading-6 text-[#637068]">
                Màn này không hiển thị số liệu mô phỏng. Khi endpoint
                observability được cấp, dữ liệu sẽ được nối vào đây với phạm vi
                tenant phù hợp.
              </p>
              <Link
                href="/knowledge"
                className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[#28765a] underline underline-offset-4"
              >
                Quản lý Knowledge Base <ArrowRight size={15} />
              </Link>
            </aside>
          </div>
        </section>
      </div>
    </main>
  );
}
