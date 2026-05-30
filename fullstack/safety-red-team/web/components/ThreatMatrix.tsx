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
      <div className="panel p-4 sm:p-5 overflow-x-auto">
        <div className="min-w-[560px]">
          <div className="grid gap-1.5 mb-1.5" style={{ gridTemplateColumns: gridCols }}>
            <div />
            {models.map((mdl) => (
              <div
                key={mdl.id}
                className="label text-center truncate px-1"
                style={{ color: hover?.m === mdl.id ? "var(--ink)" : "var(--faint)" }}
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
                className="grid gap-1.5 items-stretch"
                style={{ gridTemplateColumns: gridCols }}
              >
                <div
                  className="mono text-[11px] flex items-center justify-end pr-2 text-right"
                  style={{ color: hover?.c === cat ? "var(--ink)" : "var(--muted)" }}
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
                      className="cell-in relative h-11 rounded-md flex items-center justify-center mono text-[12px] transition-all duration-150"
                      style={{
                        animationDelay: `${ci * 30}ms`,
                        background: asrBg(v, 0.14 + v * 0.5),
                        color: v > 0.55 ? "#fff" : asrColor(v),
                        outline: isCell
                          ? "1px solid var(--ink)"
                          : isRow || isCol
                            ? "1px solid var(--line-2)"
                            : "1px solid transparent",
                        boxShadow: v > 0.5 ? `0 0 16px ${asrBg(v, v * 0.35)}` : "none",
                        opacity: dim ? 0.4 : 1,
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

          <div
            className="flex items-center gap-3 mt-4 pt-3"
            style={{ borderTop: "1px solid var(--line)" }}
          >
            <span className="label">SAFE 0%</span>
            <div
              className="h-2 flex-1 rounded-full"
              style={{ background: "linear-gradient(90deg, #1fbf75, #e8b53a, #e5484d)" }}
            />
            <span className="label" style={{ color: "var(--signal)" }}>
              100% JAILBROKEN
            </span>
          </div>
        </div>
      </div>
    </Section>
  );
}
