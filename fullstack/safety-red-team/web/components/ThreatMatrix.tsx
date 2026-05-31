"use client";

import { useState } from "react";
import { results } from "@/lib/data";
import { pct, asrColor, asrBg } from "@/lib/format";
import { Section, Card } from "./ui";

export function ThreatMatrix() {
  const { models, categories } = results;
  const [hover, setHover] = useState<{ c: string; m: string } | null>(null);
  const gridCols = `minmax(104px, 1.2fr) repeat(${models.length}, minmax(0, 1fr))`;

  return (
    <Section index="04" title="Threat matrix" kicker="attack-success by category × model">
      <Card className="overflow-x-auto p-5 sm:p-6">
        <div className="mx-auto min-w-[560px] max-w-2xl">
          <div className="mb-1.5 grid gap-1.5" style={{ gridTemplateColumns: gridCols }}>
            <div />
            {models.map((mdl) => (
              <div
                key={mdl.id}
                className="label truncate px-1 text-center transition-colors"
                style={{
                  color: hover?.m === mdl.id ? "var(--color-foreground)" : undefined,
                }}
                title={mdl.id}
              >
                {mdl.label}
              </div>
            ))}
          </div>

          <div className="space-y-1.5">
            {categories.map((cat) => (
              <div
                key={cat}
                className="grid items-stretch gap-1.5"
                style={{ gridTemplateColumns: gridCols }}
              >
                <div
                  className="mono flex items-center justify-end pr-2 text-right text-xs transition-colors"
                  style={{
                    color:
                      hover?.c === cat
                        ? "var(--color-foreground)"
                        : "var(--color-muted-foreground)",
                  }}
                >
                  {cat}
                </div>
                {models.map((mdl, ci) => {
                  const v = mdl.by_category[cat] ?? 0;
                  const isRow = hover?.c === cat;
                  const isCol = hover?.m === mdl.id;
                  const isCell = isRow && isCol;
                  const dim = hover && !isRow && !isCol;
                  return (
                    <button
                      key={mdl.id}
                      onMouseEnter={() => setHover({ c: cat, m: mdl.id })}
                      onMouseLeave={() => setHover(null)}
                      className="mono relative flex h-11 items-center justify-center rounded-md text-[11px] font-medium transition-all duration-150"
                      style={{
                        animation: "reveal 500ms cubic-bezier(0.16, 1, 0.3, 1) both",
                        animationDelay: `${ci * 30}ms`,
                        background: asrBg(v, 0.1 + v * 0.32),
                        color: v > 0.55 ? "#0a0a0a" : asrColor(v),
                        outline: isCell
                          ? "1.5px solid var(--color-foreground)"
                          : isRow || isCol
                            ? "1px solid var(--color-border)"
                            : "1px solid transparent",
                        outlineOffset: "-1px",
                        opacity: dim ? 0.35 : 1,
                      }}
                      title={`${mdl.label} × ${cat}: ${pct(v)} ASR`}
                    >
                      {pct(v)}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>

          <div className="mt-6 flex items-center gap-3 border-t border-border/60 pt-5">
            <span className="label">safe 0%</span>
            <div
              className="h-1.5 flex-1 rounded-sm"
              style={{
                background:
                  "linear-gradient(90deg, var(--color-safe), var(--color-warn), var(--color-danger))",
              }}
            />
            <span className="label" style={{ color: "var(--color-danger)" }}>
              100% jailbroken
            </span>
          </div>
        </div>
      </Card>
    </Section>
  );
}
