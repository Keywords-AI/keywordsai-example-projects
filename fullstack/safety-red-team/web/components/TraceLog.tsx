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
  const [expanded, setExpanded] = useState(false);

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

  const LIMIT = 4;
  const shown = expanded ? filtered : filtered.slice(0, LIMIT);

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
                <Badge variant={a.verdict === "unsafe" ? "unsafe" : "safe"}>
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

          {filtered.length === 0 && (
            <div className="mono py-12 text-center text-xs text-muted-foreground">
              no attempts match these filters.
            </div>
          )}
        </div>

        {filtered.length > LIMIT && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="mono mt-4 flex w-full items-center justify-center gap-1.5 rounded-lg border border-border bg-muted/30 px-3 py-2.5 text-xs text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
          >
            {expanded ? "Show less" : `Show ${filtered.length - LIMIT} more`}
            <svg
              viewBox="0 0 24 24"
              className={`size-3.5 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>
        )}
      </Card>
    </Section>
  );
}
