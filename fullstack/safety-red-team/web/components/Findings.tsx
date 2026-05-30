import { results } from "@/lib/data";
import { Section } from "./ui";

export function Findings() {
  return (
    <Section index="01" title="Key findings" kicker="auto-generated from the run">
      <ol className="space-y-3">
        {results.findings.map((f, i) => (
          <li
            key={i}
            className="reveal flex gap-4 panel px-5 py-4"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="mono text-sm pt-0.5" style={{ color: "var(--signal)" }}>
              {String(i + 1).padStart(2, "0")}
            </span>
            <p className="text-[15px] leading-relaxed" style={{ color: "var(--ink)" }}>
              {f}
            </p>
          </li>
        ))}
      </ol>
    </Section>
  );
}
