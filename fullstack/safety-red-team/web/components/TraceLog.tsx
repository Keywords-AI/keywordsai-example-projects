"use client";

import { useMemo, useState } from "react";
import { results } from "@/lib/data";
import { usd, ms } from "@/lib/format";
import { Section, Pill, Redacted } from "./ui";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

type Verdict = "all" | "safe" | "unsafe";

function Chips({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="label shrink-0">{label}</span>
      {options.map((o) => {
        const active = o === value;
        return (
          <button
            key={o}
            onClick={() => onChange(o)}
            className="mono text-xs border border-border px-3 py-1.5 transition-colors"
            style={{
              color: active ? "var(--accent)" : "var(--muted-foreground)",
              background: active ? "transparent" : "transparent",
              borderColor: active ? "var(--accent)" : "var(--border)",
            }}
          >
            {o}
          </button>
        );
      })}
    </div>
  );
}

export function TraceLog() {
  const { attempts, models, categories, attacks } = results;
  const [model, setModel] = useState("all");
  const [cat, setCat] = useState("all");
  const [atk, setAtk] = useState("all");
  const [verdict, setVerdict] = useState<Verdict>("all");

  const filtered = useMemo(
    () =>
      attempts.filter(
        (a) =>
          (model === "all" || a.model_label === model) &&
          (cat === "all" || a.category === cat) &&
          (atk === "all" || a.attack === atk) &&
          (verdict === "all" || a.verdict === verdict),
      ),
    [attempts, model, cat, atk, verdict],
  );

  const shown = filtered.slice(0, 80);

  return (
    <Section index="05" title="Trace log" kicker={`${filtered.length} of ${attempts.length} attempts`}>
      <div className="border border-border p-6 space-y-6">
        <div className="flex flex-col gap-4 pb-4 border-b border-border">
          <Chips
            label="verdict"
            options={["all", "unsafe", "safe"]}
            value={verdict}
            onChange={(v) => setVerdict(v as Verdict)}
          />
          <Chips
            label="model"
            options={["all", ...models.map((m) => m.label)]}
            value={model}
            onChange={setModel}
          />
          <Chips label="category" options={["all", ...categories]} value={cat} onChange={setCat} />
          <Chips label="framing" options={["all", ...attacks]} value={atk} onChange={setAtk} />
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Verdict</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Attack</TableHead>
                <TableHead>Judge</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead>Cost</TableHead>
                <TableHead>Prompt</TableHead>
                <TableHead>Response</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {shown.length > 0 ? (
                shown.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>
                      <Pill tone={a.verdict}>{a.verdict.toUpperCase()}</Pill>
                    </TableCell>
                    <TableCell className="font-semibold text-foreground">{a.model_label}</TableCell>
                    <TableCell>
                      <Pill>{a.category}</Pill>
                    </TableCell>
                    <TableCell>
                      <Pill>{a.attack}</Pill>
                    </TableCell>
                    <TableCell className="mono text-xs text-muted-foreground">{a.judge_score.toFixed(2)}</TableCell>
                    <TableCell className="mono text-xs text-muted-foreground">{ms(a.latency_ms)}</TableCell>
                    <TableCell className="mono text-xs text-muted-foreground">{usd(a.cost_usd)}</TableCell>
                    <TableCell className="mono text-xs text-muted-foreground truncate max-w-xs">{a.prompt_preview}</TableCell>
                    <TableCell>
                      {a.verdict === "unsafe" ? (
                        <Redacted />
                      ) : (
                        <span className="mono text-xs text-muted-foreground truncate max-w-xs">↳ {a.response_preview}</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <a
                        href={a.respan_log_url}
                        target="_blank"
                        rel="noreferrer"
                        className="underline-accent text-muted-foreground hover:text-foreground text-xs"
                      >
                        trace ↗
                      </a>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-8 text-muted-foreground">
                    no attempts match these filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {filtered.length > shown.length && (
          <div className="mono text-xs text-muted-foreground border-t border-border pt-4">
            + {filtered.length - shown.length} more attempts match. Narrow the filters to see them.
          </div>
        )}
      </div>
    </Section>
  );
}
