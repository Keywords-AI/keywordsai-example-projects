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
    <section id={id} className="reveal py-28 border-b border-border" style={{ scrollMarginTop: 72 }}>
      <div className="flex items-baseline gap-4 pb-6 mb-12">
        <span className="label">{index}</span>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-sans-tight font-semibold leading-tight tracking-tighter">{title}</h2>
        {kicker && <span className="label ml-auto hidden sm:block text-xs">{kicker}</span>}
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
    default: { color: "var(--muted-foreground)" },
    unsafe: { color: "#FF6B6B" },
    safe: { color: "#31DE4B" },
  };
  return (
    <span
      title={title}
      className="mono inline-flex items-center border border-border px-2 py-1 text-xs whitespace-nowrap"
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
    <div className="h-1 w-full overflow-hidden bg-muted">
      <div
        className="h-full"
        style={{
          width: `${Math.max(2, value * 100)}%`,
          background: color,
          animation: `underlineScale 0.9s cubic-bezier(0.2, 0.7, 0.2, 1) both`,
          animationDelay: `${delay}ms`,
        }}
      />
    </div>
  );
}

export function Redacted() {
  return <span className="mono text-xs px-2 py-1 border border-accent text-accent">▮ REDACTED</span>;
}
