import { results, overallASR, rankedBySafety } from "@/lib/data";
import { usd, asrColor } from "@/lib/format";
import { CountUp } from "./CountUp";
import { Card, Bar } from "./ui";

function ArrowUpRight() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="size-3.5 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M7 17 17 7M8 7h9v9" />
    </svg>
  );
}

function Tile({
  label,
  sub,
  value,
  color,
  kind,
  meter,
}: {
  label: string;
  sub?: string;
  value: number;
  color: string;
  kind: "pct" | "int";
  meter?: number;
}) {
  return (
    <Card className="group min-w-0 p-5 transition-colors duration-200 hover:border-border/90">
      <div className="flex items-center gap-2">
        {meter != null && (
          <span className="size-1.5 rounded-full" style={{ background: color }} />
        )}
        <span className="label">{label}</span>
      </div>
      <div
        className="mono mt-3 text-4xl font-semibold tracking-tight"
        style={{ color }}
      >
        <CountUp value={value} kind={kind} />
      </div>
      {sub && (
        <div className="mono mt-1.5 truncate text-xs text-muted-foreground">{sub}</div>
      )}
      {meter != null && <Bar value={meter} color={color} className="mt-4" delay={300} />}
    </Card>
  );
}

export function Hero() {
  const m = results.meta;
  const ranked = rankedBySafety(results.models);
  const safest = ranked[0];
  const weakest = ranked[ranked.length - 1];
  const asr = overallASR(results);

  return (
    <header className="pt-16 pb-4 sm:pt-24">
      <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-[1.5fr_1fr] lg:gap-14">
        <div className="reveal min-w-0">
          <div className="mb-6 flex items-center gap-2.5">
            <span className="label">LLM safety evaluation</span>
            <span className="size-1 rounded-full bg-subtle" />
            <span className="mono text-[11px] text-subtle">{m.generated_at.slice(0, 10)}</span>
          </div>

          <h1 className="text-5xl font-semibold leading-[1.04] tracking-tight sm:text-6xl lg:text-7xl">
            The Safety
            <br />
            Scorecard<span className="text-accent">.</span>
          </h1>

          <p className="mt-7 max-w-xl text-[0.95rem] leading-relaxed text-muted-foreground">
            {m.n_models} open models, red-teamed with {m.n_attacks} jailbreak framings across{" "}
            {m.n_behaviors} harmful behaviors. Every call is routed and judged through the{" "}
            <span className="text-foreground">Respan gateway</span>, scored by{" "}
            <span className="mono text-foreground">{m.judge}</span>. Harmful outputs are redacted.
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-3 text-xs">
            <a
              href="https://respan.ai"
              target="_blank"
              rel="noreferrer"
              className="group mono inline-flex items-center gap-1 font-medium text-foreground"
            >
              respan.ai <ArrowUpRight />
            </a>
            <a
              href={`https://${m.source_repo}`}
              target="_blank"
              rel="noreferrer"
              className="group mono link inline-flex items-center gap-1"
            >
              PAIR replication <ArrowUpRight />
            </a>
          </div>
        </div>

        <Card className="reveal min-w-0 p-6" style={{ animationDelay: "80ms" }}>
          <div className="mb-4">
            <span className="label">run manifest</span>
          </div>
          <dl className="mono divide-y divide-border/60 text-sm">
            {(
              [
                ["models", String(m.n_models)],
                ["behaviors", String(m.n_behaviors)],
                ["framings", String(m.n_attacks)],
                ["attempts", String(m.total_attempts)],
                ["strategy", m.strategy],
                ["judge", m.judge],
                ["est. cost", usd(m.total_cost_usd)],
              ] as const
            ).map(([k, v]) => (
              <div key={k} className="flex items-baseline justify-between gap-4 py-2.5">
                <dt className="shrink-0 text-muted-foreground">{k}</dt>
                <dd className="min-w-0 flex-1 truncate text-right text-foreground">{v}</dd>
              </div>
            ))}
          </dl>
        </Card>
      </div>

      <div
        className="reveal mt-10 grid grid-cols-2 gap-3 lg:grid-cols-4"
        style={{ animationDelay: "160ms" }}
      >
        <Tile label="overall ASR" value={asr} color={asrColor(asr)} kind="pct" meter={asr} />
        <Tile
          label="most resistant"
          sub={safest.label}
          value={safest.jailbreak_rate}
          color={asrColor(safest.jailbreak_rate)}
          kind="pct"
          meter={safest.jailbreak_rate}
        />
        <Tile
          label="least resistant"
          sub={weakest.label}
          value={weakest.jailbreak_rate}
          color={asrColor(weakest.jailbreak_rate)}
          kind="pct"
          meter={weakest.jailbreak_rate}
        />
        <Tile
          label="total queries"
          value={m.total_attempts}
          color="var(--color-foreground)"
          kind="int"
        />
      </div>
    </header>
  );
}
