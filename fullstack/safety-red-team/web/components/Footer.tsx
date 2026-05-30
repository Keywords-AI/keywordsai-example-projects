import { results } from "@/lib/data";

export function Footer() {
  const m = results.meta;
  return (
    <footer className="mx-auto max-w-5xl px-6 sm:px-12 pb-20 pt-12 mt-12 border-t border-border">
      <div className="grid md:grid-cols-[1.5fr_1fr] gap-12">
        <div>
          <div className="font-sans-tight text-4xl sm:text-5xl font-bold leading-tight tracking-tighter">
            Respan Red-Team<span className="text-accent">.</span>
          </div>
          <p className="mt-4 max-w-lg text-base leading-relaxed text-muted-foreground">
            An LLM safety red-teaming eval that routes and judges every model call through the
            Respan gateway.
            {m.mode === "demo" &&
              " This page renders a synthetic, redacted demo run; numbers are illustrative."}
          </p>
          <div className="mt-6 flex flex-wrap gap-3 text-xs mono">
            <a href="https://respan.ai" target="_blank" rel="noreferrer" className="underline-accent text-muted-foreground hover:text-foreground">
              respan.ai ↗
            </a>
            <a href={`https://${m.source_repo}`} target="_blank" rel="noreferrer" className="underline-accent text-muted-foreground hover:text-foreground">
              PAIR replication ↗
            </a>
            <a href="https://github.com/islamborghini" target="_blank" rel="noreferrer" className="underline-accent text-muted-foreground hover:text-foreground">
              github/islamborghini ↗
            </a>
          </div>
        </div>
        <div className="mono text-xs leading-relaxed text-muted-foreground">
          <div className="label mb-3">METHODOLOGY</div>
          PAIR (Chao et al., 2023) · AdvBench behaviors · judge{" "}
          <span className="text-foreground font-semibold">{m.judge}</span> · gateway{" "}
          <span className="text-foreground font-semibold">{m.gateway}</span>.
          <br />
          <br />
          Authorized, defensive evaluation. Harmful outputs redacted by default.
        </div>
      </div>
      <div className="mt-12 text-xs mono text-muted-foreground">
        Built by Islam Assanov · {new Date(m.generated_at).getFullYear()}
      </div>
    </footer>
  );
}
