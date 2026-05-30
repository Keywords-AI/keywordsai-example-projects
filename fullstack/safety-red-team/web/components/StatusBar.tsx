import { results } from "@/lib/data";

export function StatusBar() {
  const m = results.meta;
  const isDemo = m.mode === "demo";
  const dot = isDemo ? "var(--color-warn)" : "var(--color-safe)";
  const ring = isDemo ? "rgb(245 177 61 / 0.5)" : "rgb(53 208 127 / 0.5)";

  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-5xl items-center gap-3 px-6 text-xs sm:px-12 lg:px-16">
        <div className="flex items-center gap-2.5">
          <span className="grid size-5 place-items-center rounded-md bg-accent/15 ring-1 ring-inset ring-accent/30">
            <span className="size-1.5 rounded-full bg-accent" />
          </span>
          <span className="mono font-semibold tracking-tight text-foreground">
            Respan
            <span className="px-1 text-subtle">/</span>
            <span className="text-muted-foreground">red-team</span>
          </span>
        </div>

        <span className="mono hidden truncate text-muted-foreground md:inline">
          {m.gateway}
        </span>

        <div className="mono ml-auto flex items-center gap-3 text-muted-foreground">
          <span className="hidden sm:inline">
            judge <span className="text-foreground">{m.judge}</span>
          </span>
          <span className="flex items-center gap-2 rounded-full border border-border bg-muted/40 px-2.5 py-1">
            <span
              className="size-1.5 rounded-full"
              style={{
                background: dot,
                animation: "pulse-ring 2s infinite",
                ["--pulse-color" as string]: ring,
              }}
            />
            {m.mode.toUpperCase()}
          </span>
        </div>
      </div>
    </header>
  );
}
