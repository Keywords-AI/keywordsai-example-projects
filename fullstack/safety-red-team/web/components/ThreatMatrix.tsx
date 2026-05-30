"use client";

import { useState } from "react";
import { results } from "@/lib/data";
import { pct, asrColor, asrBg } from "@/lib/format";
import { Section } from "./ui";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

export function ThreatMatrix() {
  const { models, categories } = results;
  const [hover, setHover] = useState<{ c: string; m: string } | null>(null);

  return (
    <Section index="03" title="Threat matrix" kicker="attack-success by category × model">
      <div className="border border-border overflow-x-auto p-6">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-32">Category</TableHead>
              {models.map((mdl) => (
                <TableHead
                  key={mdl.id}
                  className="text-center w-16"
                  style={{ color: hover?.m === mdl.id ? "var(--foreground)" : "var(--muted-foreground)" }}
                  title={mdl.id}
                >
                  {mdl.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {categories.map((cat) => (
              <TableRow key={cat}>
                <TableCell
                  className="mono text-xs font-semibold"
                  style={{ color: hover?.c === cat ? "var(--foreground)" : "var(--muted-foreground)" }}
                  onMouseEnter={() => setHover((h) => ({ ...h, c: cat } as any))}
                  onMouseLeave={() => setHover(null)}
                >
                  {cat}
                </TableCell>
                {models.map((mdl, ci) => {
                  const v = mdl.by_category[cat] ?? 0;
                  const isRow = hover?.c === cat;
                  const isCol = hover?.m === mdl.id;
                  const isCell = isRow && isCol;
                  const dim = hover && !isRow && !isCol;
                  return (
                    <TableCell
                      key={mdl.id}
                      className="relative h-11 flex items-center justify-center mono text-xs transition-all duration-150 p-0"
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
                        cursor: "default",
                      }}
                      title={`${mdl.label} × ${cat}: ${pct(v)} ASR`}
                      onMouseEnter={() => setHover({ c: cat, m: mdl.id })}
                      onMouseLeave={() => setHover(null)}
                    >
                      {pct(v)}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>

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
    </Section>
  );
}
