import { results, overallASR, rankedBySafety } from "@/lib/data";
import { usd, asrColor } from "@/lib/format";
import { CountUp } from "./CountUp";

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
    <div className="panel px-4 py-4">
      <div className="label">{label}</div>
      <div className="display mono text-3xl font-bold mt-2" style={{ color }}>
        <CountUp value={value} kind={kind} />
      </div>
      {sub && (
        <div className="mono text-[11px] mt-1 truncate" style={{ color: "var(--faint)" }}>
          {sub}
        </div>
      )}
    </div>
  );
}

export function Hero() {
  const m = results.meta;
  const ranked = rankedBySafety(results.models);
  const safest = ranked[0];
  const weakest = ranked[ranked.length - 1];
  const asr = overallASR(results);

  return (
    <header className="pt-12 pb-2">
      <div className="grid lg:grid-cols-[1.4fr_1fr] gap-10 items-start">
        <div className="reveal">
          <div className="label tick mb-5">
            LLM SAFETY EVALUATION · {m.generated_at.slice(0, 10)}
          </div>
          <h1 className="display font-extrabold leading-[0.92] tracking-[-0.03em] text-[clamp(2.6rem,7vw,4.6rem)]">
            The Safety
            <br />
            Scorecard<span style={{ color: "var(--signal)" }}>.</span>
          </h1>
          <p
            className="mt-6 max-w-xl text-[15px] leading-relaxed"
            style={{ color: "var(--muted)" }}
          >
            {m.n_models} open models, red-teamed with {m.n_attacks} jailbreak framings across{" "}
            {m.n_behaviors} harmful behaviors — every call routed and judged through the{" "}
            <span style={{ color: "var(--ink)" }}>Respan gateway</span>, scored by{" "}
            <span className="mono" style={{ color: "var(--ink)" }}>
              {m.judge}
            </span>
            . Harmful outputs are redacted.
          </p>
          <div className="mt-7 flex flex-wrap items-center gap-2 text-[11px] mono">
            <a
              href="https://respan.ai"
              target="_blank"
              rel="noreferrer"
              className="rounded-md border px-2.5 py-1 transition-colors"
              style={{ borderColor: "var(--line)", color: "var(--ink)" }}
            >
              respan.ai ↗
            </a>
            <a
              href={`https://${m.source_repo}`}
              target="_blank"
              rel="noreferrer"
              className="rounded-md border px-2.5 py-1"
              style={{ borderColor: "var(--line)", color: "var(--muted)" }}
            >
              PAIR replication ↗
            </a>
            {m.redacted && <span className="redaction">▮ REDACTED BY DEFAULT</span>}
          </div>
        </div>

        <div className="panel p-5 reveal" style={{ animationDelay: "80ms" }}>
          <div className="label mb-3">RUN MANIFEST</div>
          <dl className="mono text-[12.5px]">
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
                className="flex justify-between gap-4 py-1.5"
                style={{ borderTop: i === 0 ? "none" : "1px solid var(--line)" }}
              >
                <dt style={{ color: "var(--faint)" }}>{k}</dt>
                <dd className="text-right truncate" style={{ color: "var(--ink)" }}>
                  {v}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      <div className="mt-9 grid grid-cols-2 lg:grid-cols-4 gap-3">
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
          color="var(--ink)"
          kind="int"
        />
      </div>
    </header>
  );
}
