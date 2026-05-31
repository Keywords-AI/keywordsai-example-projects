import { results, rankedBySafety } from "@/lib/data";
import { pct, usd, ms, asrColor } from "@/lib/format";
import { Section, Bar, Card } from "./ui";

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-baseline gap-1.5">
      <span className="text-muted-foreground">{k}</span>
      <span className="text-foreground">{v}</span>
    </div>
  );
}

export function Leaderboard() {
  const ranked = rankedBySafety(results.models);

  return (
    <Section
      index="03"
      title="Safety leaderboard"
      kicker="ranked by attack-success rate · lower is safer"
    >
      <div className="grid grid-cols-1 gap-3">
        {ranked.map((mdl, i) => {
          const asr = mdl.jailbreak_rate;
          const color = asrColor(asr);
          return (
            <Card
              key={mdl.id}
              className="reveal p-5 transition-colors duration-200 hover:border-border/90"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-center gap-4">
                <span className="mono grid size-8 shrink-0 place-items-center rounded-lg border border-border bg-muted/50 text-sm font-semibold text-muted-foreground">
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <span className="font-semibold tracking-tight">{mdl.label}</span>
                  <div className="mono mt-0.5 truncate text-xs text-muted-foreground">
                    {mdl.id} · {mdl.family}
                  </div>
                </div>
                <div className="w-28 shrink-0 sm:w-44">
                  <div className="mb-1.5 flex items-baseline justify-between">
                    <span className="label">ASR</span>
                    <span className="mono text-lg font-semibold" style={{ color }}>
                      {pct(asr)}
                    </span>
                  </div>
                  <Bar value={asr} color={color} delay={i * 80} />
                </div>
              </div>
              <div className="mono mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-border/60 pt-4 text-xs">
                <Stat k="coverage" v={pct(mdl.coverage_rate)} />
                <Stat
                  k="q/success"
                  v={mdl.queries_per_success != null ? String(mdl.queries_per_success) : "n/a"}
                />
                <Stat k="first-try" v={pct(mdl.first_try_rate)} />
                <Stat k="latency" v={ms(mdl.avg_latency_ms)} />
                <Stat k="avg cost" v={usd(mdl.avg_cost_usd)} />
              </div>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}
