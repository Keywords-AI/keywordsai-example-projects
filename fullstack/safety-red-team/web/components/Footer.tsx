import { results } from "@/lib/data";
import { Card } from "./ui";

export function Footer() {
  const m = results.meta;
  return (
    <footer className="mx-auto max-w-5xl border-t border-border/60 px-6 pb-20 pt-14 sm:px-12 lg:px-16">
      <div className="grid grid-cols-1 gap-10 md:grid-cols-[1.5fr_1fr]">
        <div className="min-w-0">
          <div className="flex items-center gap-2.5">
            <span className="grid size-5 place-items-center rounded-md bg-accent/15 ring-1 ring-inset ring-accent/30">
              <span className="size-1.5 rounded-full bg-accent" />
            </span>
            <span className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Respan Red-Team<span className="text-accent">.</span>
            </span>
          </div>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
            An LLM safety red-teaming eval that routes and judges every model call through the
            Respan gateway.
            {m.mode === "demo" &&
              " This page renders a synthetic, redacted demo run; numbers are illustrative."}
          </p>
          <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-xs">
            <a href="https://respan.ai" target="_blank" rel="noreferrer" className="mono link">
              respan.ai ↗
            </a>
            <a
              href={`https://${m.source_repo}`}
              target="_blank"
              rel="noreferrer"
              className="mono link"
            >
              PAIR replication ↗
            </a>
            <a
              href="https://github.com/islamborghini"
              target="_blank"
              rel="noreferrer"
              className="mono link"
            >
              github/islamborghini ↗
            </a>
          </div>
        </div>

        <Card className="min-w-0 p-5">
          <div className="label mb-3">methodology</div>
          <p className="mono text-xs leading-relaxed break-words text-muted-foreground">
            PAIR (Chao et al., 2023) · AdvBench behaviors · judge{" "}
            <span className="text-foreground">{m.judge}</span> · gateway{" "}
            <span className="text-foreground">{m.gateway}</span>.
          </p>
          <p className="mono mt-3 text-xs leading-relaxed text-subtle">
            Authorized, defensive evaluation. Harmful outputs redacted by default.
          </p>
        </Card>
      </div>

      <div className="mono mt-10 text-xs text-subtle">
        Built by Islam Assanov · {new Date(m.generated_at).getFullYear()}
      </div>
    </footer>
  );
}
