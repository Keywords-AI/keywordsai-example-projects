import { results, attackAverages } from "@/lib/data";
import { pct, asrColor } from "@/lib/format";
import { Section, Bar, Card } from "./ui";

export function AttackVectors() {
  const rows = attackAverages(results);

  return (
    <Section
      index="04"
      title="Attack vectors"
      kicker="avg attack-success per framing, across models"
    >
      <Card className="divide-y divide-border/60 px-5 sm:px-6">
        {rows.map((r, i) => {
          const isCtl = r.attack === "direct";
          const color = asrColor(r.asr);
          return (
            <div
              key={r.attack}
              className="grid grid-cols-[100px_1fr_52px] items-center gap-4 py-4 sm:grid-cols-[150px_1fr_56px]"
            >
              <div className="flex min-w-0 items-center gap-2">
                <span
                  className="mono truncate text-sm"
                  style={{
                    color: isCtl ? "var(--color-muted-foreground)" : "var(--color-foreground)",
                  }}
                >
                  {r.attack}
                </span>
                {isCtl && (
                  <span className="rounded border border-border px-1 py-px text-[10px] uppercase tracking-wider text-subtle">
                    ctl
                  </span>
                )}
              </div>
              <Bar value={r.asr} color={color} delay={i * 70} />
              <span className="mono text-right text-sm font-semibold" style={{ color }}>
                {pct(r.asr)}
              </span>
            </div>
          );
        })}
      </Card>
    </Section>
  );
}
