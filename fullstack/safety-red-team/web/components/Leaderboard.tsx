import { results, rankedBySafety } from "@/lib/data";
import { pct, usd, ms, asrColor } from "@/lib/format";
import { Section, Bar, Pill } from "./ui";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

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
      <div className="border border-border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8">#</TableHead>
              <TableHead>Model</TableHead>
              <TableHead className="w-32">ASR</TableHead>
              <TableHead>Coverage</TableHead>
              <TableHead>Q/Success</TableHead>
              <TableHead>First-Try</TableHead>
              <TableHead>Latency</TableHead>
              <TableHead>Avg Cost</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ranked.map((mdl, i) => {
              const asr = mdl.jailbreak_rate;
              return (
                <TableRow key={mdl.id} className="reveal" style={{ animationDelay: `${i * 60}ms` }}>
                  <TableCell className="mono text-xs font-semibold text-muted-foreground">
                    {i + 1}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold">{mdl.label}</span>
                      {i === 0 && <Pill tone="safe">● SAFEST</Pill>}
                      {i === last && <Pill tone="unsafe">⚠ WEAKEST</Pill>}
                    </div>
                    <div className="mono text-xs text-muted-foreground truncate">
                      {mdl.id} · {mdl.family}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <span className="mono font-bold text-sm" style={{ color: asrColor(asr) }}>
                        {pct(asr)}
                      </span>
                      <Bar value={asr} color={asrColor(asr)} delay={i * 80} />
                    </div>
                  </TableCell>
                  <TableCell className="mono text-xs">{pct(mdl.coverage_rate)}</TableCell>
                  <TableCell className="mono text-xs">
                    {mdl.queries_per_success != null ? String(mdl.queries_per_success) : "n/a"}
                  </TableCell>
                  <TableCell className="mono text-xs">{pct(mdl.first_try_rate)}</TableCell>
                  <TableCell className="mono text-xs">{ms(mdl.avg_latency_ms)}</TableCell>
                  <TableCell className="mono text-xs">{usd(mdl.avg_cost_usd)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </Section>
  );
}
