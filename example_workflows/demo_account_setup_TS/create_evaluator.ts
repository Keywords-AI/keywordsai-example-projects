/**
 * Create Evaluator Example
 *
 * This example demonstrates how to create custom evaluators in KeywordsAI.
 * Evaluators are used to automatically score and evaluate logs.
 *
 * Documentation: https://docs.keywordsai.co/api-endpoints/evaluate/evaluators/create
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;

// Evaluator configuration from environment variables
const EVALUATOR_LLM_ENGINE = process.env.EVALUATOR_LLM_ENGINE || "gpt-4o-mini";
const EVALUATOR_TEMPERATURE = parseFloat(process.env.EVALUATOR_TEMPERATURE || "0.1");
const EVALUATOR_MAX_TOKENS = parseInt(process.env.EVALUATOR_MAX_TOKENS || "200");
const DEFAULT_MIN_SCORE = parseFloat(process.env.DEFAULT_MIN_SCORE || "0.0");
const DEFAULT_MAX_SCORE = parseFloat(process.env.DEFAULT_MAX_SCORE || "1.0");
const DEFAULT_PASSING_SCORE = parseFloat(process.env.DEFAULT_PASSING_SCORE || "0.7");

interface EvaluatorResponse {
  id?: string;
  evaluator_slug?: string;
  [key: string]: unknown;
}

interface CreateEvaluatorOptions {
  name: string;
  evaluatorSlug: string;
  evaluatorType: string;
  scoreValueType: string;
  description?: string;
  configurations?: Record<string, unknown>;
}

interface CreateLLMEvaluatorOptions {
  name: string;
  evaluatorSlug: string;
  evaluatorDefinition: string;
  scoringRubric: string;
  description?: string;
  minScore?: number;
  maxScore?: number;
  passingScore?: number;
  llmEngine?: string;
  modelOptions?: Record<string, unknown>;
}

/**
 * Create a custom evaluator in Keywords AI.
 */
export async function createEvaluator(options: CreateEvaluatorOptions): Promise<EvaluatorResponse> {
  const { name, evaluatorSlug, evaluatorType, scoreValueType, description = "", configurations } = options;

  const url = `${BASE_URL}/evaluators`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    name,
    evaluator_slug: evaluatorSlug,
    type: evaluatorType,
    score_value_type: scoreValueType,
    description,
  };

  if (configurations) {
    payload.configurations = configurations;
  }

  console.log("Creating evaluator...");
  console.log(`  URL: ${url}`);
  console.log(`  Name: ${name}`);
  console.log(`  Slug: ${evaluatorSlug}`);
  console.log(`  Type: ${evaluatorType}`);
  console.log(`  Score Type: ${scoreValueType}`);
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: EvaluatorResponse = await response.json();
  console.log(`\n[OK] Evaluator created successfully`);
  if (data.id) {
    console.log(`  Evaluator ID: ${data.id}`);
  }
  if (data.evaluator_slug) {
    console.log(`  Evaluator Slug: ${data.evaluator_slug}`);
  }

  return data;
}

/**
 * Create an LLM-based evaluator with custom definition and scoring rubric.
 */
export async function createLLMEvaluator(options: CreateLLMEvaluatorOptions): Promise<EvaluatorResponse> {
  const {
    name,
    evaluatorSlug,
    evaluatorDefinition,
    scoringRubric,
    description = "",
    minScore,
    maxScore,
    passingScore,
    llmEngine,
    modelOptions,
  } = options;

  // Use environment variables as defaults if not provided
  const finalMinScore = minScore !== undefined ? minScore : DEFAULT_MIN_SCORE;
  const finalMaxScore = maxScore !== undefined ? maxScore : DEFAULT_MAX_SCORE;
  const finalPassingScore = passingScore !== undefined ? passingScore : DEFAULT_PASSING_SCORE;
  const finalLlmEngine = llmEngine !== undefined ? llmEngine : EVALUATOR_LLM_ENGINE;

  const configurations: Record<string, unknown> = {
    evaluator_definition: evaluatorDefinition,
    scoring_rubric: scoringRubric,
    min_score: finalMinScore,
    max_score: finalMaxScore,
    passing_score: finalPassingScore,
    llm_engine: finalLlmEngine,
  };

  if (modelOptions) {
    configurations.model_options = modelOptions;
  }

  return createEvaluator({
    name,
    evaluatorSlug,
    evaluatorType: "llm",
    scoreValueType: "numerical",
    description,
    configurations,
  });
}

async function main() {
  const timestamp = Date.now();
  
  console.log("=".repeat(80));
  console.log("KeywordsAI Create Evaluator Example");
  console.log("=".repeat(80));

  // Example 1: Simple LLM evaluator for response quality
  console.log("\n[Example 1] Creating LLM evaluator for response quality");
  console.log("-".repeat(80));

  const evaluator1 = await createLLMEvaluator({
    name: "Response Quality Evaluator",
    evaluatorSlug: `response_quality_${timestamp}`,
    evaluatorDefinition:
      "Evaluate the quality of the assistant's response based on:\n" +
      "1. Accuracy: Is the information correct?\n" +
      "2. Relevance: Does it address the user's question?\n" +
      "3. Completeness: Is the answer thorough?\n" +
      "\n" +
      "<llm_input>{{input}}</llm_input>\n" +
      "<llm_output>{{output}}</llm_output>",
    scoringRubric: "0.0=Poor, 0.25=Below Average, 0.5=Average, 0.75=Good, 1.0=Excellent",
    description: "Evaluates response quality on a 0-1 scale",
    minScore: DEFAULT_MIN_SCORE,
    maxScore: DEFAULT_MAX_SCORE,
    passingScore: DEFAULT_PASSING_SCORE,
    modelOptions: {
      temperature: EVALUATOR_TEMPERATURE,
      max_tokens: EVALUATOR_MAX_TOKENS,
    },
  });

  // Example 2: Helpfulness evaluator with categorical scores
  console.log("\n[Example 2] Creating helpfulness evaluator (categorical)");
  console.log("-".repeat(80));

  const evaluator2 = await createEvaluator({
    name: "Helpfulness Evaluator",
    evaluatorSlug: `helpfulness_categorical_${timestamp}`,
    evaluatorType: "llm",
    scoreValueType: "categorical",
    description: "Evaluates if a response is helpful, neutral, or unhelpful",
    configurations: {
      evaluator_definition:
        "Rate whether the assistant's response is helpful, neutral, or unhelpful.\n" +
        "<llm_input>{{input}}</llm_input>\n" +
        "<llm_output>{{output}}</llm_output>",
      scoring_rubric: "helpful, neutral, unhelpful",
      llm_engine: EVALUATOR_LLM_ENGINE,
      model_options: {
        temperature: EVALUATOR_TEMPERATURE,
        max_tokens: 50,
      },
    },
  });

  // Example 3: Factual accuracy evaluator (boolean)
  console.log("\n[Example 3] Creating factual accuracy evaluator (boolean)");
  console.log("-".repeat(80));

  const evaluator3 = await createEvaluator({
    name: "Factual Accuracy Evaluator",
    evaluatorSlug: `factual_accuracy_${timestamp}`,
    evaluatorType: "llm",
    scoreValueType: "boolean",
    description: "Checks if the response contains factual inaccuracies",
    configurations: {
      evaluator_definition:
        "Determine if the assistant's response contains any factual inaccuracies.\n" +
        "Respond with 'true' if the response is factually accurate, 'false' if it contains inaccuracies.\n" +
        "\n" +
        "<llm_input>{{input}}</llm_input>\n" +
        "<llm_output>{{output}}</llm_output>",
      scoring_rubric: "true=Factually accurate, false=Contains inaccuracies",
      llm_engine: EVALUATOR_LLM_ENGINE,
      model_options: {
        temperature: 0.0,
        max_tokens: 10,
      },
    },
  });

  // Example 4: Custom numerical evaluator with 1-5 scale
  console.log("\n[Example 4] Creating custom numerical evaluator (1-5 scale)");
  console.log("-".repeat(80));

  const evaluator4 = await createLLMEvaluator({
    name: "Overall Satisfaction Evaluator",
    evaluatorSlug: `satisfaction_1_5_${timestamp}`,
    evaluatorDefinition:
      "Rate the overall satisfaction with the assistant's response on a scale of 1-5:\n" +
      "- Consider accuracy, helpfulness, clarity, and completeness\n" +
      "\n" +
      "<llm_input>{{input}}</llm_input>\n" +
      "<llm_output>{{output}}</llm_output>",
    scoringRubric: "1=Very Dissatisfied, 2=Dissatisfied, 3=Neutral, 4=Satisfied, 5=Very Satisfied",
    description: "Evaluates overall satisfaction on a 1-5 scale",
    minScore: 1.0,
    maxScore: 5.0,
    passingScore: 4.0,
    modelOptions: {
      temperature: EVALUATOR_TEMPERATURE,
      max_tokens: 100,
    },
  });

  console.log("\n" + "=".repeat(80));
  console.log("All evaluators created successfully!");
  console.log("=".repeat(80));

  return {
    evaluator_1: evaluator1,
    evaluator_2: evaluator2,
    evaluator_3: evaluator3,
    evaluator_4: evaluator4,
  };
}

// Run main only if this is the entry point (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
