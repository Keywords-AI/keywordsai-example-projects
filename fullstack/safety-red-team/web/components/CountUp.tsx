"use client";

import { useEffect, useRef, useState } from "react";
import { pct } from "@/lib/format";

// Formatting lives here (client side) so the server never passes a function
// across the RSC boundary.
const FORMATTERS: Record<string, (n: number) => string> = {
  pct: (n) => pct(n),
  int: (n) => Math.round(n).toLocaleString("en-US"),
};

export function CountUp({
  value,
  kind = "int",
  durationMs = 950,
}: {
  value: number;
  kind?: "pct" | "int";
  durationMs?: number;
}) {
  const fmt = FORMATTERS[kind];
  // SSR / no-JS renders the final value; the effect animates from 0 on mount.
  const [n, setN] = useState(value);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let raf = 0;
    const t0 = performance.now();
    setN(0);
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / durationMs);
      const eased = 1 - Math.pow(1 - p, 3);
      setN(value * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
      else setN(value);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, durationMs]);

  return <>{fmt(n)}</>;
}
