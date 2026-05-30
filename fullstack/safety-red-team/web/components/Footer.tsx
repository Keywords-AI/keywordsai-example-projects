import { results } from "@/lib/data";

const linkStyle = { borderColor: "var(--line)", color: "var(--muted)" };

export function Footer() {
  const m = results.meta;
  return (
    <footer
      className="mx-auto max-w-[1180px] px-5 pb-16 pt-10 mt-8"
      style={{ borderTop: "1px solid var(--line)" }}
    >
      <div className="grid md:grid-cols-[1.5fr_1fr] gap-8">
        <div>
          <div className="display text-lg font-bold">
            Respan Red-Team<span style={{ color: "var(--signal)" }}>.</span>
          </div>
          <p className="mt-2 max-w-md text-[13px] leading-relaxed" style={{ color: "var(--muted)" }}>
            An LLM safety red-teaming eval that routes and judges every model call through the
            Respan gateway.
            {m.mode === "demo" &&
              " This page renders a synthetic, redacted demo run — numbers are illustrative."}
          </p>
          <div className="mt-4 flex flex-wrap gap-2 text-[11px] mono">
            <a href="https://respan.ai" target="_blank" rel="noreferrer" className="rounded-md border px-2.5 py-1" style={linkStyle}>
              respan.ai ↗
            </a>
            <a href={`https://${m.source_repo}`} target="_blank" rel="noreferrer" className="rounded-md border px-2.5 py-1" style={linkStyle}>
              PAIR replication ↗
            </a>
            <a href="https://github.com/islamborghini" target="_blank" rel="noreferrer" className="rounded-md border px-2.5 py-1" style={linkStyle}>
              github/islamborghini ↗
            </a>
          </div>
        </div>
        <div className="mono text-[11px] leading-relaxed" style={{ color: "var(--faint)" }}>
          <div className="label mb-2">METHODOLOGY</div>
          PAIR (Chao et al., 2023) · AdvBench behaviors · judge{" "}
          <span style={{ color: "var(--muted)" }}>{m.judge}</span> · gateway{" "}
          <span style={{ color: "var(--muted)" }}>{m.gateway}</span>.
          <br />
          <br />
          Authorized, defensive evaluation. Harmful outputs redacted by default.
        </div>
      </div>
      <div className="mt-8 text-[11px] mono" style={{ color: "var(--faint)" }}>
        Built by Islam Assanov · {new Date(m.generated_at).getFullYear()}
      </div>
    </footer>
  );
}
