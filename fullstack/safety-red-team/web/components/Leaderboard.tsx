import { results, rankedBySafety } from "@/lib/data";
import { pct, usd, ms, asrColor } from "@/lib/format";
import { Section, Bar, Pill } from "./ui";

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <span>
      <span className="text-muted-foreground">{k} </span>
      <span className="text-foreground font-semibold">{v}</span>
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
      <div className="space-y-0">
        {ranked.map((mdl, i) => {
          const asr = mdl.jailbreak_rate;
          return (
            <div
              key={mdl.id}
              className="border-b border-border px-0 py-6 reveal"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-center gap-4 mb-4">
                <span className="mono text-sm font-semibold w-6 text-muted-foreground">
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-base">{mdl.label}</span>
                    {i === 0 && <Pill tone="safe">● SAFEST</Pill>}
                    {i === last && <Pill tone="unsafe">⚠ WEAKEST</Pill>}
                  </div>
                  <div className="mono text-xs text-muted-foreground truncate">
                    {mdl.id} · {mdl.family}
                  </div>
                </div>
                <div className="w-32 sm:w-48 shrink-0">
                  <div className="flex justify-between items-baseline mb-2">
                    <span className="label">ASR</span>
                    <span className="mono font-bold text-lg" style={{ color: asrColor(asr) }}>
                      {pct(asr)}
                    </span>
                  </div>
                  <Bar value={asr} color={asrColor(asr)} delay={i * 80} />
                </div>
              </div>
              <div className="flex flex-wrap gap-x-6 gap-y-2 mono text-xs border-t border-border pt-4">
                <Stat k="coverage" v={pct(mdl.coverage_rate)} />
                <Stat
                  k="q/success"
                  v={mdl.queries_per_success != null ? String(mdl.queries_per_success) : "n/a"}
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
