/**
 * Create Log Scores Example
 *
 * This example demonstrates how to create scores on logs using evaluators.
 * Scores link evaluators to specific log entries and store evaluation results.
 *
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
  categorical_value?: string[];
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

interface BatchScoreItem {
  log_id: string;
  evaluator_slug: string;
  score: number | string | boolean | unknown[];
  reasoning?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Create a score on a specific log using an evaluator.
 */
export async function createLogScore(options: CreateLogScoreOptions): Promise<ScoreResponse> {
  const { logId, evaluatorSlug, evaluatorId, score, reasoning, metadata, scoreType = "numerical" } = options;

  const url = `${BASE_URL}/scores`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    log_id: logId,
  };

  // Use evaluator_id if provided, otherwise use evaluator_slug
  if (evaluatorId) {
    payload.evaluator_id = evaluatorId;
  }
  if (evaluatorSlug) {
    payload.evaluator_slug = evaluatorSlug;
  }

  // Add the appropriate value field based on score_type
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
    default:
      payload.numerical_value = Number(score);
  }

  if (reasoning) {
    payload.reasoning = reasoning;
  }
  if (metadata) {
    payload.metadata = metadata;
  }

  console.log("Creating log score...");
  console.log(`  URL: ${url}`);
  console.log(`  Log ID: ${logId}`);
  console.log(`  Evaluator Slug: ${evaluatorSlug}`);
  console.log(`  Score: ${score}`);
  if (reasoning) {
    const truncatedReasoning = reasoning.length > 100 ? `${reasoning.substring(0, 100)}...` : reasoning;
    console.log(`  Reasoning: ${truncatedReasoning}`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
  }

  const data: ScoreResponse = await response.json();
  console.log(`\n[OK] Score created successfully`);
  if (data.id) {
    console.log(`  Score ID: ${data.id}`);
  }
  // Check for different value types
  if (data.numerical_value !== undefined && data.numerical_value !== null) {
    console.log(`  Score Value (numerical): ${data.numerical_value}`);
  } else if (data.string_value) {
    console.log(`  Score Value (string): ${data.string_value}`);
  } else if (data.boolean_value !== undefined && data.boolean_value !== null) {
    console.log(`  Score Value (boolean): ${data.boolean_value}`);
  } else if (data.categorical_value) {
    console.log(`  Score Value (categorical): ${data.categorical_value}`);
  }

  return data;
}

/**
 * Create multiple scores in a single batch request.
 */
export async function createLogScoreBatch(scores: BatchScoreItem[]): Promise<Record<string, unknown>> {
  const url = `${BASE_URL}/evaluate/log-scores/create-batch`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload = {
    scores,
  };

  console.log("Creating batch log scores...");
  console.log(`  URL: ${url}`);
  console.log(`  Number of scores: ${scores.length}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log(`\n[OK] Batch scores created successfully`);
  if (data.created !== undefined) {
    console.log(`  Created: ${data.created}`);
  }
  if (data.failed !== undefined) {
    console.log(`  Failed: ${data.failed}`);
  }

  return data;
}

async function main() {
  console.log("=".repeat(80));
  console.log("KeywordsAI Create Log Scores Example");
  console.log("=".repeat(80));
  console.log("\n[NOTE] This example requires existing logs and evaluators.");
  console.log("   Please run basic_logging.ts and create_evaluator.ts first.\n");

  // Example 1: Create a single score
  console.log("[Example 1] Creating a single score on a log");
  console.log("-".repeat(80));
  console.log("\nTo create a score, you need:");
  console.log("  1. A log ID (from basic_logging.ts or list_request_logs.ts)");
  console.log("  2. An evaluator slug (from create_evaluator.ts)");
  console.log("\nExample code:");
  console.log("-".repeat(80));

  const exampleCode1 = `
    // Replace these with actual values from your account
    const logId = "your-log-unique-id-here";
    const evaluatorSlug = "response_quality";  // From create_evaluator.ts

    const scoreData = await createLogScore({
      logId: logId,
      evaluatorSlug: evaluatorSlug,
      score: 0.85,
      reasoning: "The response is accurate, relevant, and provides a complete answer to the user's question."
    });
    `;
  console.log(exampleCode1);

  // Example 2: Create score with metadata
  console.log("\n[Example 2] Creating a score with metadata");
  console.log("-".repeat(80));
  console.log("\nExample code:");
  console.log("-".repeat(80));

  const exampleCode2 = `
    const scoreData = await createLogScore({
      logId: "your-log-unique-id-here",
      evaluatorSlug: "response_quality",
      score: 0.92,
      reasoning: "Excellent response with high accuracy and helpfulness.",
      metadata: {
        evaluated_by: "human_reviewer_001",
        evaluation_date: "2024-01-15",
        confidence: 0.95
      }
    });
    `;
  console.log(exampleCode2);

  // Example 3: Create batch scores
  console.log("\n[Example 3] Creating multiple scores in batch");
  console.log("-".repeat(80));
  console.log("\nExample code:");
  console.log("-".repeat(80));

  const exampleCode3 = `
    const scores = [
      {
        log_id: "log-id-1",
        evaluator_slug: "response_quality",
        score: 0.85,
        reasoning: "Good response quality"
      },
      {
        log_id: "log-id-2",
        evaluator_slug: "response_quality",
        score: 0.92,
        reasoning: "Excellent response quality"
      },
      {
        log_id: "log-id-1",
        evaluator_slug: "factual_accuracy",
        score: true,  // For boolean evaluators
        reasoning: "No factual inaccuracies detected"
      }
    ];

    const batchResult = await createLogScoreBatch(scores);
    `;
  console.log(exampleCode3);

  // Example 4: Complete workflow example
  console.log("\n[Example 4] Complete workflow");
  console.log("-".repeat(80));
  console.log("\nThis shows the complete workflow:");
  console.log("  1. Create logs");
  console.log("  2. Create evaluators");
  console.log("  3. List logs to get log IDs");
  console.log("  4. Create scores on logs");
  console.log("-".repeat(80));

  const workflowCode = `
    // Step 1: Create a log (from basic_logging.ts)
    import { createLog } from "./basic_logging";
    const logData = await createLog({
      model: "gpt-4o",
      inputMessages: [{ role: "user", content: "What is Python?" }],
      outputMessage: { role: "assistant", content: "Python is a programming language..." },
      customIdentifier: "python_question_001"
    });
    const logId = logData.unique_id;

    // Step 2: Create an evaluator (from create_evaluator.ts)
    import { createLLMEvaluator } from "./create_evaluator";
    const evaluatorData = await createLLMEvaluator({
      name: "Response Quality",
      evaluatorSlug: "response_quality",
      evaluatorDefinition: "Evaluate response quality...",
      scoringRubric: "0.0=Poor, 1.0=Excellent"
    });
    const evaluatorSlug = evaluatorData.evaluator_slug;

    // Step 3: Create a score on the log
    import { createLogScore } from "./create_log_scores";
    const scoreData = await createLogScore({
      logId: logId,
      evaluatorSlug: evaluatorSlug,
      score: 0.88,
      reasoning: "The response accurately explains Python as a programming language."
    });
    `;
  console.log(workflowCode);

  console.log("\n" + "=".repeat(80));
  console.log("Examples completed! Use these patterns with your actual log IDs and evaluator slugs.");
  console.log("=".repeat(80));
}

// Run main only if this is the entry point (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
