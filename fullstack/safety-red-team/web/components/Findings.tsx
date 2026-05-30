import { results } from "@/lib/data";
import { Section } from "./ui";
import { Card } from "./ui/card";

export function Findings() {
  return (
    <Section index="01" title="Key findings" kicker="auto-generated from the run">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {results.findings.map((f, i) => (
          <Card
            key={i}
            className="reveal p-4"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="flex gap-4">
              <span className="text-accent font-bold text-lg flex-shrink-0 pt-1">
                {i + 1}.
              </span>
              <p className="text-base leading-relaxed text-foreground">
                {f}
              </p>
            </div>
          </Card>
        ))}
      </div>
    </Section>
  );
}
