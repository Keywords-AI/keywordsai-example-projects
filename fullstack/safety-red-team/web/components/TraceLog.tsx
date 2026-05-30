"use client";

import { useMemo, useState } from "react";
import { results } from "@/lib/data";
import { usd, ms } from "@/lib/format";
import { Section, Badge, Redacted, Toggle, Card } from "./ui";

type Verdict = "all" | "safe" | "unsafe";

function FilterRow({
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
      <span className="label w-16 shrink-0">{label}</span>
      <div className="flex flex-wrap items-center gap-1.5">
        {options.map((o) => (
          <Toggle key={o} active={o === value} onClick={() => onChange(o)}>
            {o}
          </Toggle>
        ))}
      </div>
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
    <Section
      index="05"
      title="Trace log"
      kicker={`${filtered.length} of ${attempts.length} attempts`}
    >
      <Card className="p-5 sm:p-6">
        <div className="flex flex-col gap-3 border-b border-border/60 pb-5">
          <FilterRow
            label="verdict"
            options={["all", "unsafe", "safe"]}
            value={verdict}
            onChange={(v) => setVerdict(v as Verdict)}
          />
          <FilterRow
            label="model"
            options={["all", ...models.map((m) => m.label)]}
            value={model}
            onChange={setModel}
          />
          <FilterRow label="category" options={["all", ...categories]} value={cat} onChange={setCat} />
          <FilterRow label="framing" options={["all", ...attacks]} value={atk} onChange={setAtk} />
        </div>

        <div className="divide-y divide-border/60">
          {shown.map((a) => (
            <div
              key={a.id}
              className="group -mx-3 space-y-2 rounded-lg px-3 py-4 transition-colors hover:bg-muted/30"
            >
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <Badge variant={a.verdict === "unsafe" ? "unsafe" : "safe"} dot>
                  {a.verdict}
                </Badge>
                <span className="font-semibold tracking-tight">{a.model_label}</span>
                <Badge>{a.category}</Badge>
                <Badge>{a.attack}</Badge>
                <span className="mono text-muted-foreground">judge {a.judge_score.toFixed(2)}</span>
                <span className="mono text-muted-foreground">{ms(a.latency_ms)}</span>
                <span className="mono text-muted-foreground">{usd(a.cost_usd)}</span>
                <a
                  href={a.respan_log_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mono link ml-auto inline-flex items-center gap-1"
                >
                  trace ↗
                </a>
              </div>
              <div className="flex min-w-0 flex-col gap-2 text-xs sm:flex-row sm:items-center">
                <span
                  className="mono min-w-0 flex-1 truncate text-muted-foreground"
                  title={a.prompt_preview}
                >
                  {a.prompt_preview}
                </span>
                {a.verdict === "unsafe" ? (
                  <Redacted />
                ) : (
                  <span
                    className="mono min-w-0 flex-1 truncate text-subtle"
                    title={a.response_preview}
                  >
                    ↳ {a.response_preview}
                  </span>
                )}
              </div>
            </div>
          ))}

          {filtered.length > shown.length && (
            <div className="mono pt-5 text-xs text-muted-foreground">
              + {filtered.length - shown.length} more attempts match. Narrow the filters to see them.
            </div>
          )}
          {filtered.length === 0 && (
            <div className="mono py-12 text-center text-xs text-muted-foreground">
              no attempts match these filters.
            </div>
          )}
        </div>
      </Card>
    </Section>
  );
}
