/**
 * Test script for creating log scores - complete end-to-end workflow.
 */

import "dotenv/config";
import { createLog } from "./basic_logging.js";
import { createLLMEvaluator } from "./create_evaluator.js";
import { createLogScore } from "./create_log_scores.js";

const TEST_MODEL = process.env.TEST_MODEL || "gpt-4o";

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  console.log("Test Create Log Score - Complete Workflow\n");

  // Step 1: Create a log
  console.log("[1] Creating log...");
  const logData = await createLog({
    model: TEST_MODEL,
    inputMessages: [{ role: "user", content: "What is machine learning?" }],
    outputMessage: {
      role: "assistant",
      content: "Machine learning is a subset of AI that enables systems to learn from experience.",
    },
    customIdentifier: `test_score_log_${Date.now()}`,
  });
  const logId = logData.unique_id;

  // Step 2: Create an evaluator
  console.log("\n[2] Creating evaluator...");
  const evaluatorData = await createLLMEvaluator({
    name: "Test Response Quality Evaluator",
    evaluatorSlug: `test_response_quality_${Date.now()}`,
    evaluatorDefinition:
      "Evaluate response quality based on accuracy.\n" +
      "<llm_input>{{input}}</llm_input>\n<llm_output>{{output}}</llm_output>",
    scoringRubric: "0.0=Poor, 0.5=Average, 1.0=Excellent",
  });
  const evaluatorSlug = evaluatorData.evaluator_slug;
  const evaluatorId = evaluatorData.id;

  // Step 3: Wait for processing
  console.log("\n[3] Waiting 2s for processing...");
  await sleep(2000);

  // Step 4: Create score
  console.log("\n[4] Creating score...");
  if (!logId || !evaluatorId) {
    throw new Error("Log ID or Evaluator ID is missing");
  }

  await createLogScore({
    logId,
    evaluatorId,
    evaluatorSlug,
    score: 0.85,
    reasoning: "The response accurately explains machine learning.",
  });

  console.log("\nTest completed successfully!");
}

main().catch(console.error);
