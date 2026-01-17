/**
 * Test script for creating log scores.
 * This demonstrates the complete end-to-end workflow.
 */

import "dotenv/config";
import { createLog } from "./basic_logging.js";
import { createLLMEvaluator } from "./create_evaluator.js";
import { createLogScore } from "./create_log_scores.js";

// Test configuration from environment variables
const TEST_MODEL = process.env.TEST_MODEL || "gpt-4o";
const TEST_EVALUATOR_TEMPERATURE = parseFloat(process.env.TEST_EVALUATOR_TEMPERATURE || "0.1");
const TEST_EVALUATOR_MAX_TOKENS = parseInt(process.env.TEST_EVALUATOR_MAX_TOKENS || "200");

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  console.log("=".repeat(80));
  console.log("Testing Create Log Score - Complete Workflow");
  console.log("=".repeat(80));

  // Step 1: Create a log
  console.log("\n[Step 1] Creating a log...");
  const logData = await createLog({
    model: TEST_MODEL,
    inputMessages: [{ role: "user", content: "What is machine learning?" }],
    outputMessage: {
      role: "assistant",
      content:
        "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
    },
    customIdentifier: `test_score_log_${Date.now()}`,
  });
  const logId = logData.unique_id;
  console.log(`[OK] Log created with ID: ${logId}`);

  // Step 2: Create an evaluator
  console.log("\n[Step 2] Creating an evaluator...");
  const evaluatorData = await createLLMEvaluator({
    name: "Test Response Quality Evaluator",
    evaluatorSlug: `test_response_quality_${Date.now()}`,
    evaluatorDefinition:
      "Evaluate the response quality based on accuracy and completeness.\n" +
      "<llm_input>{{input}}</llm_input>\n" +
      "<llm_output>{{output}}</llm_output>",
    scoringRubric: "0.0=Poor, 0.5=Average, 1.0=Excellent",
    description: "Test evaluator for log scoring",
    modelOptions: {
      temperature: TEST_EVALUATOR_TEMPERATURE,
      max_tokens: TEST_EVALUATOR_MAX_TOKENS,
    },
  });
  const evaluatorSlug = evaluatorData.evaluator_slug;
  const evaluatorId = evaluatorData.id;
  console.log(`[OK] Evaluator created with slug: ${evaluatorSlug}, ID: ${evaluatorId}`);

  // Step 3: Wait a moment
  console.log("\n[Waiting] Waiting 2 seconds for processing...");
  await sleep(2000);

  // Step 4: Create a score on the log
  console.log("\n[Step 3] Creating score on the log...");
  try {
    if (!logId || !evaluatorId) {
      throw new Error("Log ID or Evaluator ID is missing");
    }

    const scoreData = await createLogScore({
      logId: logId,
      evaluatorId: evaluatorId,
      evaluatorSlug: evaluatorSlug,
      score: 0.85,
      reasoning:
        "The response accurately explains machine learning and provides a clear, complete definition.",
    });

    console.log(`\n[SUCCESS] Score created!`);
    console.log(`Score ID: ${scoreData.id || "N/A"}`);
    // Show the correct value field
    if (scoreData.numerical_value !== undefined && scoreData.numerical_value !== null) {
      console.log(`Score Value (numerical): ${scoreData.numerical_value}`);
    } else if (scoreData.string_value) {
      console.log(`Score Value (string): ${scoreData.string_value}`);
    } else if (scoreData.boolean_value !== undefined && scoreData.boolean_value !== null) {
      console.log(`Score Value (boolean): ${scoreData.boolean_value}`);
    }
    console.log(`\n${"=".repeat(80)}`);
    console.log("Test completed successfully!");
    console.log("=".repeat(80));
  } catch (error) {
    console.log(`\n[ERROR] Error creating score: ${error}`);
    if (error instanceof Error) {
      console.error(error.stack);
    }
  }
}

// Run main if this is the entry point
main().catch(console.error);
