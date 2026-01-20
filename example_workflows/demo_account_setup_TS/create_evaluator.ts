/**
 * Create Evaluator Example
 * Documentation: https://docs.keywordsai.co/api-endpoints/evaluate/evaluators/create
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;
const EVALUATOR_LLM_ENGINE = process.env.EVALUATOR_LLM_ENGINE || "gpt-4o-mini";

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
  modelOptions?: Record<string, unknown>;
}

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
  if (configurations) payload.configurations = configurations;

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: EvaluatorResponse = await response.json();
  console.log(`[OK] Evaluator created: ${data.evaluator_slug || data.id}`);
  return data;
}

export async function createLLMEvaluator(options: CreateLLMEvaluatorOptions): Promise<EvaluatorResponse> {
  const {
    name,
    evaluatorSlug,
    evaluatorDefinition,
    scoringRubric,
    description = "",
    minScore = 0.0,
    maxScore = 1.0,
    passingScore = 0.7,
    modelOptions,
  } = options;

  const configurations: Record<string, unknown> = {
    evaluator_definition: evaluatorDefinition,
    scoring_rubric: scoringRubric,
    min_score: minScore,
    max_score: maxScore,
    passing_score: passingScore,
    llm_engine: EVALUATOR_LLM_ENGINE,
  };
  if (modelOptions) configurations.model_options = modelOptions;

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
  console.log("Create Evaluator Example\n");

  // LLM evaluator for response quality
  console.log("[1] Response quality evaluator (numerical)");
  await createLLMEvaluator({
    name: "Response Quality Evaluator",
    evaluatorSlug: `response_quality_${timestamp}`,
    evaluatorDefinition:
      "Evaluate response quality based on accuracy, relevance, and completeness.\n" +
      "<llm_input>{{input}}</llm_input>\n<llm_output>{{output}}</llm_output>",
    scoringRubric: "0.0=Poor, 0.5=Average, 1.0=Excellent",
    description: "Evaluates response quality on a 0-1 scale",
  });

  // Categorical evaluator
  console.log("\n[2] Helpfulness evaluator (categorical)");
  await createEvaluator({
    name: "Helpfulness Evaluator",
    evaluatorSlug: `helpfulness_${timestamp}`,
    evaluatorType: "llm",
    scoreValueType: "categorical",
    description: "Evaluates if response is helpful, neutral, or unhelpful",
    configurations: {
      evaluator_definition:
        "Rate whether the response is helpful, neutral, or unhelpful.\n" +
        "<llm_input>{{input}}</llm_input>\n<llm_output>{{output}}</llm_output>",
      scoring_rubric: "helpful, neutral, unhelpful",
      llm_engine: EVALUATOR_LLM_ENGINE,
    },
  });

  // Boolean evaluator
  console.log("\n[3] Factual accuracy evaluator (boolean)");
  await createEvaluator({
    name: "Factual Accuracy Evaluator",
    evaluatorSlug: `factual_accuracy_${timestamp}`,
    evaluatorType: "llm",
    scoreValueType: "boolean",
    description: "Checks for factual inaccuracies",
    configurations: {
      evaluator_definition:
        "Determine if the response contains factual inaccuracies.\n" +
        "<llm_input>{{input}}</llm_input>\n<llm_output>{{output}}</llm_output>",
      scoring_rubric: "true=Factually accurate, false=Contains inaccuracies",
      llm_engine: EVALUATOR_LLM_ENGINE,
    },
  });

  console.log("\nDone.");
}

const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
