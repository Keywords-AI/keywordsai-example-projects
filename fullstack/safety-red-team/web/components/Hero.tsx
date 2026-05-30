import { results, overallASR, rankedBySafety } from "@/lib/data";
import { usd, asrColor } from "@/lib/format";
import { CountUp } from "./CountUp";
import { Card } from "./ui/card";

function Tile({
  label,
  sub,
  value,
  color,
  kind,
}: {
  label: string;
  sub?: string;
  value: number;
  color: string;
  kind: "pct" | "int";
}) {
  return (
    <Card className="p-6 relative">
      <div className="absolute top-0 left-0 h-1 w-16 bg-accent" />
      <div className="label mb-3">{label}</div>
      <div className="mono text-4xl lg:text-5xl font-bold" style={{ color }}>
        <CountUp value={value} kind={kind} />
      </div>
      {sub && (
        <div className="mono text-xs mt-2 text-muted-foreground truncate">{sub}</div>
      )}
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
    <header className="pt-20 pb-6">
      <div className="grid lg:grid-cols-[1.4fr_1fr] gap-12 items-start">
        <div className="reveal">
          <div className="label mb-6">LLM SAFETY EVALUATION · {m.generated_at.slice(0, 10)}</div>
          <h1 className="font-sans-tight font-bold leading-none tracking-tighter text-6xl sm:text-7xl lg:text-8xl mb-8">
            The Safety<br />Scorecard<span className="text-accent">.</span>
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-muted-foreground mb-8">
            {m.n_models} open models, red-teamed with {m.n_attacks} jailbreak framings across {m.n_behaviors} harmful behaviors. Every call is routed and judged through the <span className="text-foreground">Respan gateway</span>, scored by{" "}
            <span className="mono text-foreground">
              {m.judge}
            </span>
            . Harmful outputs are redacted.
          </p>
          <div className="flex flex-wrap items-center gap-3 text-xs mono">
            <a
              href="https://respan.ai"
              target="_blank"
              rel="noreferrer"
              className="underline-accent text-foreground"
            >
              respan.ai ↗
            </a>
            <a
              href={`https://${m.source_repo}`}
              target="_blank"
              rel="noreferrer"
              className="underline-accent text-muted-foreground hover:text-foreground"
            >
              PAIR replication ↗
            </a>
            {m.redacted && <span className="mono text-xs px-2 py-1 border border-accent text-accent">▮ REDACTED</span>}
          </div>
        </div>

        <Card className="p-8 reveal" style={{ animationDelay: "80ms" }}>
          <div className="label mb-4">RUN MANIFEST</div>
          <dl className="mono text-sm space-y-3">
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
            ).map(([k, v], i) => (
              <div
                key={k}
                className="flex justify-between gap-4 py-2"
                style={{ borderTop: i === 0 ? "none" : `1px solid var(--border)` }}
              >
                <dt className="text-muted-foreground">{k}</dt>
                <dd className="text-right truncate text-foreground">{v}</dd>
              </div>
            ))}
          </dl>
        </Card>
      </div>

      <div className="mt-12 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Tile label="OVERALL ASR" value={asr} color={asrColor(asr)} kind="pct" />
        <Tile
          label="MOST RESISTANT"
          sub={safest.label}
          value={safest.jailbreak_rate}
          color={asrColor(safest.jailbreak_rate)}
          kind="pct"
        />
        <Tile
          label="LEAST RESISTANT"
          sub={weakest.label}
          value={weakest.jailbreak_rate}
          color={asrColor(weakest.jailbreak_rate)}
          kind="pct"
        />
        <Tile
          label="TOTAL QUERIES"
          value={m.total_attempts}
          color="var(--foreground)"
          kind="int"
        />
      </div>
    </header>
  );
}
