"use client";

import { useMemo, useState } from "react";
import { results } from "@/lib/data";
import { usd, ms } from "@/lib/format";
import { Section, Pill, Redacted } from "./ui";

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
      <div className="border border-border p-6">
        <div className="flex flex-col gap-4 pb-6 mb-4 border-b border-border">
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

        <div className="space-y-0">
          {shown.map((a) => (
            <div
              key={a.id}
              className="py-6 space-y-2 border-t border-border"
            >
              <div className="flex flex-wrap items-center gap-2 text-xs mono">
                <Pill tone={a.verdict}>{a.verdict.toUpperCase()}</Pill>
                <span className="text-foreground font-semibold">{a.model_label}</span>
                <Pill>{a.category}</Pill>
                <Pill>{a.attack}</Pill>
                <span className="text-muted-foreground">judge {a.judge_score.toFixed(2)}</span>
                <span className="text-muted-foreground">{ms(a.latency_ms)}</span>
                <span className="text-muted-foreground">{usd(a.cost_usd)}</span>
                <a
                  href={a.respan_log_url}
                  target="_blank"
                  rel="noreferrer"
                  className="ml-auto underline-accent text-muted-foreground hover:text-foreground"
                >
                  trace ↗
                </a>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-xs min-w-0">
                <span
                  className="mono truncate flex-1 min-w-0 text-muted-foreground"
                  title={a.prompt_preview}
                >
                  {a.prompt_preview}
                </span>
                {a.verdict === "unsafe" ? (
                  <Redacted />
                ) : (
                  <span
                    className="mono truncate flex-1 min-w-0 text-muted-foreground"
                    title={a.response_preview}
                  >
                    ↳ {a.response_preview}
                  </span>
                )}
              </div>
            </div>
          ))}
          {filtered.length > shown.length && (
            <div
              className="pt-6 mono text-xs text-muted-foreground border-t border-border"
            >
              + {filtered.length - shown.length} more attempts match. Narrow the filters to see them.
            </div>
          )}
          {filtered.length === 0 && (
            <div className="py-12 text-center mono text-xs text-muted-foreground">
              no attempts match these filters.
            </div>
          )}
        </div>
      </div>
    </Section>
  );
}
