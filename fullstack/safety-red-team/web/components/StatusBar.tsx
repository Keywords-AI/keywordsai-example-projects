import { results } from "@/lib/data";

export function StatusBar() {
  const m = results.meta;

  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-5xl items-center gap-3 px-6 text-xs sm:px-12 lg:px-16">
        <span className="mono font-semibold tracking-tight text-foreground">
          Respan
          <span className="px-1 text-subtle">/</span>
          <span className="text-muted-foreground">red-team</span>
        </span>

        <span className="mono hidden truncate text-muted-foreground md:inline">
          {m.gateway}
        </span>

        <div className="mono ml-auto flex items-center gap-3 text-muted-foreground">
          <span className="hidden sm:inline">
            judge <span className="text-foreground">{m.judge}</span>
          </span>
        </div>
      </div>
    </header>
  );
}
