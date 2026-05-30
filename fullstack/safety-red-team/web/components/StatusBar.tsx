import { results } from "@/lib/data";

export function StatusBar() {
  const m = results.meta;
  return (
    <div className="sticky top-0 z-30 border-b border-border bg-background">
      <div className="mx-auto max-w-5xl px-6 sm:px-12 h-12 flex items-center gap-4 text-xs mono">
        <div className="flex items-center gap-2 text-foreground">
          <span
            className="inline-block w-2 h-2"
            style={{ background: "var(--accent)" }}
          />
          <span className="tracking-wider">
            RESPAN<span className="text-muted-foreground">/</span>RED-TEAM
          </span>
        </div>
        <span className="hidden md:inline truncate text-muted-foreground">
          {m.gateway}
        </span>
        <div className="ml-auto flex items-center gap-4 text-muted-foreground">
          <span className="hidden sm:inline">
            JUDGE <span className="text-foreground font-semibold">{m.judge}</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block w-1.5 h-1.5 rounded-full bg-yellow-500"
              style={{
                animation: "pulse 2s infinite",
                boxShadow: "0 0 0 0 rgba(250, 204, 21, 0.45)",
              }}
            />
            {m.mode.toUpperCase()}
          </span>
        </div>
      </div>
      <style>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0.45); }
          70% { box-shadow: 0 0 0 6px rgba(250, 204, 21, 0); }
          100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0); }
        }
      `}</style>
    </div>
  );
}
