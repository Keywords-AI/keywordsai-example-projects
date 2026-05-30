import type { HTMLAttributes, ReactNode } from "react";

/** Tiny class joiner — no runtime dep needed for this surface. */
export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

/* ------------------------------------------------------------------ *
 * Card — the base surface. Subtle border, faint elevation, soft radius.
 * ------------------------------------------------------------------ */
export function Card({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card text-card-foreground elevated",
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------ *
 * Badge — compact status / metadata chip.
 * ------------------------------------------------------------------ */
type BadgeVariant = "default" | "safe" | "unsafe" | "warn" | "accent" | "outline";

const BADGE_VARIANTS: Record<BadgeVariant, string> = {
  default: "border-border bg-muted/60 text-muted-foreground",
  outline: "border-border bg-transparent text-muted-foreground",
  safe: "border-safe/25 bg-safe/10 text-safe",
  unsafe: "border-danger/25 bg-danger/10 text-danger",
  warn: "border-warn/25 bg-warn/10 text-warn",
  accent: "border-accent/30 bg-accent/10 text-accent",
};

export function Badge({
  variant = "default",
  dot = false,
  className,
  children,
  title,
}: {
  variant?: BadgeVariant;
  dot?: boolean;
  className?: string;
  children: ReactNode;
  title?: string;
}) {
  return (
    <span
      title={title}
      className={cn(
        "mono inline-flex items-center gap-1.5 whitespace-nowrap rounded-md border px-2 py-0.5 text-[11px] font-medium leading-5",
        BADGE_VARIANTS[variant],
        className,
      )}
    >
      {dot && <span className="size-1.5 shrink-0 rounded-full bg-current" />}
      {children}
    </span>
  );
}

/* ------------------------------------------------------------------ *
 * Section — page section with an indexed, minimal header.
 * ------------------------------------------------------------------ */
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
    <section
      id={id}
      className="reveal scroll-mt-24 border-t border-border/60 py-16 sm:py-20"
    >
      <div className="mb-10 flex flex-wrap items-end justify-between gap-x-4 gap-y-2">
        <div className="flex items-center gap-3">
          <span className="mono rounded-md border border-border bg-muted/40 px-2 py-1 text-[11px] leading-none text-muted-foreground">
            {index}
          </span>
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            {title}
          </h2>
        </div>
        {kicker && (
          <span className="max-w-xs text-right text-xs text-muted-foreground">
            {kicker}
          </span>
        )}
      </div>
      {children}
    </section>
  );
}

/* ------------------------------------------------------------------ *
 * Bar — rounded, animated progress meter.
 * ------------------------------------------------------------------ */
export function Bar({
  value,
  color,
  delay = 0,
  className,
}: {
  value: number;
  color: string;
  delay?: number;
  className?: string;
}) {
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-muted", className)}>
      <div
        className="h-full origin-left rounded-full"
        style={{
          width: `${Math.max(2, value * 100)}%`,
          background: color,
          animation: "bar-grow 0.9s cubic-bezier(0.2, 0.7, 0.2, 1) both",
          animationDelay: `${delay}ms`,
        }}
      />
    </div>
  );
}

/* ------------------------------------------------------------------ *
 * Toggle — single filter chip (used in filter groups).
 * ------------------------------------------------------------------ */
export function Toggle({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      data-active={active}
      className={cn(
        "mono cursor-pointer rounded-md border px-2.5 py-1 text-xs transition-colors duration-150",
        active
          ? "border-foreground/20 bg-muted text-foreground shadow-sm"
          : "border-border bg-transparent text-muted-foreground hover:border-border hover:bg-muted/50 hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------ *
 * Redacted — marks withheld harmful output.
 * ------------------------------------------------------------------ */
export function Redacted() {
  return (
    <Badge variant="accent">
      <svg
        viewBox="0 0 24 24"
        className="size-3"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        <rect x="4" y="11" width="16" height="9" rx="2" />
        <path d="M8 11V8a4 4 0 0 1 8 0v3" />
      </svg>
      redacted
    </Badge>
  );
}
