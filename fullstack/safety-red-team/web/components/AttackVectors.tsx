import { results, attackAverages } from "@/lib/data";
import { pct, asrColor } from "@/lib/format";
import { Section, Bar } from "./ui";

export function AttackVectors() {
  const rows = attackAverages(results);

  return (
    <Section
      index="04"
      title="Attack vectors"
      kicker="avg attack-success per framing, across models"
    >
      <div className="panel p-5 space-y-4">
        {rows.map((r, i) => (
          <div
            key={r.attack}
            className="grid grid-cols-[96px_1fr_48px] sm:grid-cols-[130px_1fr_56px] items-center gap-4"
          >
            <span
              className="mono text-[13px] truncate"
              style={{ color: r.attack === "direct" ? "var(--faint)" : "var(--ink)" }}
            >
              {r.attack}
              {r.attack === "direct" ? " ·ctl" : ""}
            </span>
            <Bar value={r.asr} color={asrColor(r.asr)} delay={i * 70} />
            <span
              className="mono text-[13px] text-right"
              style={{ color: asrColor(r.asr) }}
            >
              {pct(r.asr)}
            </span>
          </div>
        ))}
      </div>
    </Section>
  );
}
