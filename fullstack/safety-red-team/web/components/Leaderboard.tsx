import { results, rankedBySafety } from "@/lib/data";
import { pct, usd, ms, asrColor } from "@/lib/format";
import { Section, Bar, Pill } from "./ui";

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <span>
      <span style={{ color: "var(--faint)" }}>{k} </span>
      <span style={{ color: "var(--ink)" }}>{v}</span>
    </span>
  );
}

export function Leaderboard() {
  const ranked = rankedBySafety(results.models);
  const last = ranked.length - 1;

  return (
    <Section
      index="02"
      title="Safety leaderboard"
      kicker="ranked by attack-success rate · lower is safer"
    >
      <div className="space-y-2.5">
        {ranked.map((mdl, i) => {
          const asr = mdl.jailbreak_rate;
          return (
            <div
              key={mdl.id}
              className="panel px-4 py-3.5 reveal"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-center gap-4">
                <span className="mono text-sm w-5 text-right" style={{ color: "var(--faint)" }}>
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{mdl.label}</span>
                    {i === 0 && <Pill tone="safe">● SAFEST</Pill>}
                    {i === last && <Pill tone="unsafe">⚠ WEAKEST</Pill>}
                  </div>
                  <div className="mono text-[11px] truncate" style={{ color: "var(--faint)" }}>
                    {mdl.id} · {mdl.family}
                  </div>
                </div>
                <div className="w-[130px] sm:w-[210px] shrink-0">
                  <div className="flex justify-between items-baseline mb-1.5">
                    <span className="label">ASR</span>
                    <span className="mono font-bold text-[15px]" style={{ color: asrColor(asr) }}>
                      {pct(asr)}
                    </span>
                  </div>
                  <Bar value={asr} color={asrColor(asr)} delay={i * 80} />
                </div>
              </div>
              <div
                className="mt-3 pt-3 flex flex-wrap gap-x-6 gap-y-1 mono text-[11px]"
                style={{ borderTop: "1px solid var(--line)" }}
              >
                <Stat k="coverage" v={pct(mdl.coverage_rate)} />
                <Stat
                  k="q/success"
                  v={mdl.queries_per_success != null ? String(mdl.queries_per_success) : "—"}
                />
                <Stat k="first-try" v={pct(mdl.first_try_rate)} />
                <Stat k="latency" v={ms(mdl.avg_latency_ms)} />
                <Stat k="avg cost" v={usd(mdl.avg_cost_usd)} />
              </div>
            </div>
          );
        })}
      </div>
    </Section>
  );
}
