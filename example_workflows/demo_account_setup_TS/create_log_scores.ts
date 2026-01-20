/**
 * Create Log Scores Example
 * Documentation: https://docs.keywordsai.co/api-endpoints/evaluate/log-scores/create
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;

interface ScoreResponse {
  id?: string;
  numerical_value?: number;
  string_value?: string;
  boolean_value?: boolean;
  [key: string]: unknown;
}

interface CreateLogScoreOptions {
  logId: string;
  evaluatorSlug?: string;
  evaluatorId?: string;
  score: number | string | boolean | unknown[];
  reasoning?: string;
  metadata?: Record<string, unknown>;
  scoreType?: "numerical" | "string" | "boolean" | "categorical" | "json";
}

export async function createLogScore(options: CreateLogScoreOptions): Promise<ScoreResponse> {
  const { logId, evaluatorSlug, evaluatorId, score, reasoning, metadata, scoreType = "numerical" } = options;

  const url = `${BASE_URL}/scores`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = { log_id: logId };
  if (evaluatorId) payload.evaluator_id = evaluatorId;
  if (evaluatorSlug) payload.evaluator_slug = evaluatorSlug;

  switch (scoreType) {
    case "numerical":
      payload.numerical_value = Number(score);
      break;
    case "string":
      payload.string_value = String(score);
      break;
    case "boolean":
      payload.boolean_value = Boolean(score);
      break;
    case "categorical":
      payload.categorical_value = Array.isArray(score) ? score : [score];
      break;
    case "json":
      payload.json_value = typeof score === "string" ? score : JSON.stringify(score);
      break;
  }

  if (reasoning) payload.reasoning = reasoning;
  if (metadata) payload.metadata = metadata;

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
  }

  const data: ScoreResponse = await response.json();
  const value = data.numerical_value ?? data.string_value ?? data.boolean_value ?? "N/A";
  console.log(`[OK] Score created: ${data.id} (value: ${value})`);
  return data;
}

async function main() {
  console.log("Create Log Scores Example\n");
  console.log("This example requires existing logs and evaluators.");
  console.log("Run basic_logging.ts and create_evaluator.ts first.\n");

  console.log("Usage:");
  console.log(`
  import { createLogScore } from "./create_log_scores.js";

  await createLogScore({
    logId: "your-log-id",
    evaluatorSlug: "response_quality",
    evaluatorId: "your-evaluator-id",
    score: 0.85,
    reasoning: "Good response quality"
  });
  `);
}

const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
