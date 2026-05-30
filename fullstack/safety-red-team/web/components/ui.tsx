import type { CSSProperties, ReactNode } from "react";

export function Section({
  index,
  title,
  kicker,
  children,
  id,
}: {
  index: string;
  title: string;
  kicker?: string;
  children: ReactNode;
  id?: string;
}) {
  return (
    <section id={id} className="reveal" style={{ scrollMarginTop: 72 }}>
      <div
        className="flex items-baseline gap-4 pb-3 mb-7 border-b"
        style={{ borderColor: "var(--line)" }}
      >
        <span className="label">{index}</span>
        <h2 className="display text-xl sm:text-2xl font-bold">{title}</h2>
        {kicker && <span className="label ml-auto hidden sm:block">{kicker}</span>}
      </div>
      {children}
    </section>
  );
}

export function Pill({
  tone = "default",
  children,
  title,
}: {
  tone?: "default" | "unsafe" | "safe";
  children: ReactNode;
  title?: string;
}) {
  const styles: Record<string, CSSProperties> = {
    default: { color: "var(--muted)", borderColor: "var(--line)", background: "var(--panel-2)" },
    unsafe: { color: "#ff8a8a", borderColor: "rgba(255,77,77,0.32)", background: "rgba(255,77,77,0.08)" },
    safe: { color: "#5fd6a0", borderColor: "rgba(31,191,117,0.32)", background: "rgba(31,191,117,0.08)" },
  };
  return (
    <span
      title={title}
      className="mono inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] whitespace-nowrap"
      style={styles[tone]}
    >
      {children}
    </span>
  );
}

export function Bar({
  value,
  color,
  delay = 0,
}: {
  value: number;
  color: string;
  delay?: number;
}) {
  return (
    <div className="h-2 w-full rounded-full overflow-hidden" style={{ background: "var(--panel-2)" }}>
      <div
        className="h-full rounded-full bar-fill"
        style={{ width: `${Math.max(2, value * 100)}%`, background: color, animationDelay: `${delay}ms` }}
      />
    </div>
  );
}

export function Redacted() {
  return <span className="redaction">▮ REDACTED</span>;
}
