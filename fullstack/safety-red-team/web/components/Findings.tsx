import { results } from "@/lib/data";
import { Section } from "./ui";

export function Findings() {
  return (
    <Section index="01" title="Key findings" kicker="auto-generated from the run">
      <ol className="space-y-0">
        {results.findings.map((f, i) => (
          <li
            key={i}
            className="reveal flex gap-4 border-b border-border px-0 py-6"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="mono text-base font-semibold text-accent flex-shrink-0">
              {String(i + 1).padStart(2, "0")}
            </span>
            <p className="text-base leading-relaxed text-foreground">
              {f}
            </p>
          </li>
        ))}
      </ol>
    </Section>
  );
}
