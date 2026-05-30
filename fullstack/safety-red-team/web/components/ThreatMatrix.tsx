"use client";

import { useState } from "react";
import { results } from "@/lib/data";
import { pct, asrColor, asrBg } from "@/lib/format";
import { Section } from "./ui";

export function ThreatMatrix() {
  const { models, categories } = results;
  const [hover, setHover] = useState<{ c: string; m: string } | null>(null);
  const gridCols = `minmax(112px, 1.3fr) repeat(${models.length}, minmax(0, 1fr))`;

  return (
    <Section index="03" title="Threat matrix" kicker="attack-success by category × model">
      <div className="border border-border p-6 overflow-x-auto">
        <div className="min-w-[560px]">
          <div className="grid gap-1 mb-1" style={{ gridTemplateColumns: gridCols }}>
            <div />
            {models.map((mdl) => (
              <div
                key={mdl.id}
                className="label text-center truncate px-1"
                style={{ color: hover?.m === mdl.id ? "var(--foreground)" : "var(--muted-foreground)" }}
                title={mdl.id}
              >
                {mdl.label}
              </div>
            ))}
          </div>

          <div className="space-y-1">
            {categories.map((cat) => (
              <div
                key={cat}
                className="grid gap-1 items-stretch"
                style={{ gridTemplateColumns: gridCols }}
              >
                <div
                  className="mono text-xs flex items-center justify-end pr-2 text-right"
                  style={{ color: hover?.c === cat ? "var(--foreground)" : "var(--muted-foreground)" }}
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
                      className="relative h-11 flex items-center justify-center mono text-xs transition-all duration-150"
                      style={{
                        animation: `reveal 500ms cubic-bezier(0.25, 0, 0, 1) both`,
                        animationDelay: `${ci * 30}ms`,
                        background: asrBg(v, 0.08 + v * 0.3),
                        color: v > 0.55 ? "#000" : asrColor(v),
                        border: isCell
                          ? "1px solid var(--foreground)"
                          : isRow || isCol
                            ? "1px solid var(--border)"
                            : "1px solid transparent",
                        opacity: dim ? 0.3 : 1,
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

          <div className="flex items-center gap-3 mt-6 pt-4 border-t border-border">
            <span className="label">SAFE 0%</span>
            <div
              className="h-1 flex-1"
              style={{ background: "linear-gradient(90deg, #31DE4B, #FFC107, #FF3D00)" }}
            />
            <span className="label text-accent">
              100% JAILBROKEN
            </span>
          </div>
        </div>
      </div>
    </Section>
  );
}
