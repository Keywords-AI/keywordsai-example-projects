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
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="label mr-1 shrink-0">{label}</span>
      {options.map((o) => {
        const active = o === value;
        return (
          <button
            key={o}
            onClick={() => onChange(o)}
            className="mono text-[11px] rounded-md border px-2 py-0.5 transition-colors"
            style={{
              color: active ? "#0a0b0e" : "var(--muted)",
              background: active ? "var(--ink)" : "transparent",
              borderColor: active ? "var(--ink)" : "var(--line)",
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
      <div className="panel p-4 sm:p-5">
        <div
          className="flex flex-col gap-2.5 pb-4 mb-2"
          style={{ borderBottom: "1px solid var(--line)" }}
        >
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

        <div>
          {shown.map((a) => (
            <div
              key={a.id}
              className="py-3 grid gap-2"
              style={{ borderTop: "1px solid var(--line)" }}
            >
              <div className="flex flex-wrap items-center gap-2 text-[12px] mono">
                <Pill tone={a.verdict}>{a.verdict.toUpperCase()}</Pill>
                <span style={{ color: "var(--ink)" }}>{a.model_label}</span>
                <Pill>{a.category}</Pill>
                <Pill>{a.attack}</Pill>
                <span style={{ color: "var(--faint)" }}>judge {a.judge_score.toFixed(2)}</span>
                <span style={{ color: "var(--faint)" }}>{ms(a.latency_ms)}</span>
                <span style={{ color: "var(--faint)" }}>{usd(a.cost_usd)}</span>
                <a
                  href={a.respan_log_url}
                  target="_blank"
                  rel="noreferrer"
                  className="ml-auto"
                  style={{ color: "var(--muted)" }}
                >
                  trace ↗
                </a>
              </div>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 text-[12px] min-w-0">
                <span
                  className="mono truncate flex-1 min-w-0"
                  style={{ color: "var(--muted)" }}
                  title={a.prompt_preview}
                >
                  {a.prompt_preview}
                </span>
                {a.verdict === "unsafe" ? (
                  <Redacted />
                ) : (
                  <span
                    className="mono truncate flex-1 min-w-0"
                    style={{ color: "var(--faint)" }}
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
              className="pt-3 mono text-[11px]"
              style={{ color: "var(--faint)", borderTop: "1px solid var(--line)" }}
            >
              + {filtered.length - shown.length} more attempts match. Narrow the filters to see them.
            </div>
          )}
          {filtered.length === 0 && (
            <div className="py-8 text-center mono text-[12px]" style={{ color: "var(--faint)" }}>
              no attempts match these filters.
            </div>
          )}
        </div>
      </div>
    </Section>
  );
}
