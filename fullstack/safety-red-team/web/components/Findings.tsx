import { results } from "@/lib/data";
import { Section } from "./ui";

export function Findings() {
  return (
    <Section index="01" title="Key findings" kicker="auto-generated from the run">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {results.findings.map((f, i) => (
          <div
            key={i}
            className="reveal group flex items-start gap-4 rounded-xl border border-border bg-card/50 px-5 py-4 transition-colors duration-200 hover:border-border/90 hover:bg-card"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="mono mt-0.5 grid size-7 shrink-0 place-items-center rounded-md border border-border bg-muted/50 text-xs font-semibold text-muted-foreground transition-colors group-hover:text-foreground">
              {String(i + 1).padStart(2, "0")}
            </span>
            <p className="text-sm leading-relaxed text-foreground/90">{f}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
