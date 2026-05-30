import { results } from "@/lib/data";

export function StatusBar() {
  const m = results.meta;
  return (
    <div
      className="sticky top-0 z-30 border-b backdrop-blur-md"
      style={{ borderColor: "var(--line)", background: "rgba(10,11,14,0.72)" }}
    >
      <div className="mx-auto max-w-[1180px] px-5 h-10 flex items-center gap-4 text-[11px] mono">
        <div className="flex items-center gap-2">
          <span
            className="inline-block w-2.5 h-2.5 rounded-[3px]"
            style={{ background: "var(--signal)" }}
          />
          <span className="tracking-[0.2em]">
            RESPAN<span style={{ color: "var(--faint)" }}>/</span>RED-TEAM
          </span>
        </div>
        <span className="hidden md:inline truncate" style={{ color: "var(--faint)" }}>
          {m.gateway}
        </span>
        <div className="ml-auto flex items-center gap-4" style={{ color: "var(--muted)" }}>
          <span className="hidden sm:inline">
            JUDGE <span style={{ color: "var(--ink)" }}>{m.judge}</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="live-dot" /> {m.mode.toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}
