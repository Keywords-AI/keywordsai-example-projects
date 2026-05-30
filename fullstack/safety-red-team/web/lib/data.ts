import raw from "@/data/results.json";
import type { Results, ModelRow } from "./types";

export const results = raw as unknown as Results;

export function rankedBySafety(models: ModelRow[]): ModelRow[] {
  return [...models].sort((a, b) => a.jailbreak_rate - b.jailbreak_rate);
}

export interface AttackAvg {
  attack: string;
  asr: number;
}

export function attackAverages(r: Results): AttackAvg[] {
  return r.attacks
    .map((attack) => ({
      attack,
      asr:
        r.models.reduce((s, m) => s + (m.by_attack[attack] ?? 0), 0) /
        r.models.length,
    }))
    .sort((a, b) => b.asr - a.asr);
}

export function overallASR(r: Results): number {
  const unsafe = r.attempts.filter((a) => a.verdict === "unsafe").length;
  return r.attempts.length ? unsafe / r.attempts.length : 0;
}

export function categoryAverage(r: Results, category: string): number {
  const vals = r.models.map((m) => m.by_category[category] ?? 0);
  return vals.reduce((s, v) => s + v, 0) / (vals.length || 1);
}
