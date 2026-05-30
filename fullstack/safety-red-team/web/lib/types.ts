export interface Meta {
  generated_at: string;
  mode: "demo" | "live";
  gateway: string;
  judge: string;
  strategy: string;
  pair_available: boolean;
  n_models: number;
  n_behaviors: number;
  n_attacks: number;
  total_attempts: number;
  total_cost_usd: number;
  redacted: boolean;
  trace_group: string;
  source_repo: string;
}

export interface ModelRow {
  id: string;
  label: string;
  family: string;
  attempts: number;
  jailbreaks: number;
  behaviors: number;
  behaviors_broken: number;
  /** ASR, the attack-success rate (unsafe attempts / total attempts). Headline metric. */
  jailbreak_rate: number;
  /** behaviors broken by >=1 framing / behaviors */
  coverage_rate: number;
  safe_rate: number;
  queries_per_success: number | null;
  first_try_rate: number;
  avg_latency_ms: number;
  avg_cost_usd: number;
  by_category: Record<string, number>;
  by_attack: Record<string, number>;
}

export interface Attempt {
  id: string;
  model_id: string;
  model_label: string;
  behavior_id: string;
  category: string;
  attack: string;
  verdict: "safe" | "unsafe";
  judge_score: number;
  latency_ms: number;
  cost_usd: number;
  prompt_preview: string;
  response_preview: string;
  respan_log_url: string;
}

export interface Results {
  meta: Meta;
  categories: string[];
  attacks: string[];
  models: ModelRow[];
  findings: string[];
  attempts: Attempt[];
}
