import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import { createOpenAI } from "@ai-sdk/openai";
import { Respan } from "@respan/respan";
import { VercelAIInstrumentor } from "@respan/instrumentation-vercel";

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: resolve(__dirname, "../../../.env"), override: true });

const modelName = process.env.RESPAN_MODEL || "gpt-4o-mini";
const embeddingModelName = process.env.RESPAN_EMBEDDING_MODEL || "text-embedding-3-small";
const respanBaseUrl = process.env.RESPAN_BASE_URL || "https://api.respan.ai";
const gatewayBaseUrl =
  process.env.RESPAN_GATEWAY_BASE_URL ||
  process.env.RESPAN_BASE_URL ||
  "https://api.respan.ai/api";
const gatewayApiKey =
  process.env.RESPAN_GATEWAY_API_KEY ||
  process.env.OPENAI_API_KEY ||
  process.env.RESPAN_API_KEY;

assert.ok(process.env.RESPAN_API_KEY, "RESPAN_API_KEY must be set in repo-root .env");
assert.ok(gatewayApiKey, "RESPAN_GATEWAY_API_KEY, OPENAI_API_KEY, or RESPAN_API_KEY must be set");

export async function runVercelCase(caseId, fn) {
  const runId = `vercel-${caseId}-${Date.now()}`;
  const gateway = createOpenAI({
    apiKey: gatewayApiKey,
    baseURL: gatewayBaseUrl,
  });
  const respan = new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: respanBaseUrl,
    appName: `vercel-${caseId}`,
    instrumentations: [new VercelAIInstrumentor()],
    traceContent: true,
    silenceInitializationMessage: false,
  });

  const telemetry = (scenario, metadata = {}) => ({
    isEnabled: true,
    functionId: `vercel_${caseId}_${scenario}`,
    metadata: {
      run_id: runId,
      scenario,
      case_id: caseId,
      customer_params: JSON.stringify({
        customer_identifier: `customer-${runId}`,
        email: "vercel-unit@example.com",
        name: "Vercel Unit Case",
      }),
      thread_identifier: `thread-${runId}`,
      session_identifier: `session-${runId}`,
      trace_group_identifier: `trace-group-${runId}`,
      ...metadata,
    },
  });

  console.log("============================================================");
  console.log(`Vercel AI SDK live case: ${caseId}`);
  console.log(`run_id: ${runId}`);
  console.log(`model: ${modelName}`);
  console.log(`embedding_model: ${embeddingModelName}`);
  console.log(`respan_base_url: ${respanBaseUrl}`);
  console.log(`gateway_base_url: ${gatewayBaseUrl}`);
  console.log("============================================================");

  await respan.initialize();

  try {
    await respan.withWorkflow(
      {
        name: `vercel_${caseId}.workflow`,
        associationProperties: {
          run_id: runId,
          case_id: caseId,
          framework: "vercel-ai-sdk",
          instrumentation: "respan-instrumentation-vercel",
        },
      },
      async () => {
        await fn({
          gateway,
          modelName,
          embeddingModelName,
          runId,
          telemetry,
        });
      }
    );
  } finally {
    await respan.shutdown();
  }

  console.log("============================================================");
  console.log(`Live case complete: ${caseId}`);
  console.log(`Find on Respan platform by run_id: ${runId}`);
  console.log("============================================================");

  return runId;
}
