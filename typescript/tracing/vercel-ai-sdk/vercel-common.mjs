import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import { createOpenAI } from "@ai-sdk/openai";
import { OpenTelemetry } from "@ai-sdk/otel";
import { registerTelemetry } from "ai";
import { Respan } from "@respan/respan";
import { VercelAIInstrumentor } from "@respan/instrumentation-vercel";

const DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai";
const DEFAULT_GATEWAY_BASE_URL = "https://api.respan.ai/api";
const __dirname = dirname(fileURLToPath(import.meta.url));

let envLoaded = false;
let telemetryRegistered = false;

function loadEnv() {
  if (envLoaded) return;
  let current = __dirname;
  for (let depth = 0; depth < 8; depth += 1) {
    const envPath = join(current, ".env");
    if (existsSync(envPath)) {
      dotenv.config({ path: envPath, override: false, quiet: true });
      envLoaded = true;
      return;
    }
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  dotenv.config({ override: false, quiet: true });
  envLoaded = true;
}

function ensureTelemetryRegistered() {
  if (telemetryRegistered) return;
  registerTelemetry(new OpenTelemetry({
    embedding: true,
    providerMetadata: true,
    schema: true,
    toolChoice: true,
    usage: true,
  }));
  telemetryRegistered = true;
}

export async function runVercelCase(caseId, fn) {
  loadEnv();

  const runId = `vercel-ai-sdk-ts-${caseId}-${Date.now()}`;
  const respanApiKey = process.env.RESPAN_API_KEY;
  const gatewayApiKey = process.env.RESPAN_GATEWAY_API_KEY ?? respanApiKey;
  const respanBaseURL = process.env.RESPAN_BASE_URL ?? DEFAULT_RESPAN_BASE_URL;
  const gatewayBaseURL =
    process.env.RESPAN_GATEWAY_BASE_URL ??
    process.env.OPENAI_BASE_URL ??
    DEFAULT_GATEWAY_BASE_URL;
  const modelName = process.env.RESPAN_MODEL ?? "gpt-4o-mini";
  const embeddingModelName = process.env.RESPAN_EMBEDDING_MODEL ?? "text-embedding-3-small";

  assert.ok(respanApiKey, "RESPAN_API_KEY must be set in respan-example-projects/.env");
  assert.ok(gatewayApiKey, "RESPAN_GATEWAY_API_KEY or RESPAN_API_KEY must be set");

  const gateway = createOpenAI({
    apiKey: gatewayApiKey,
    baseURL: gatewayBaseURL,
  });
  const respan = new Respan({
    apiKey: respanApiKey,
    baseURL: respanBaseURL,
    appName: `vercel-ai-sdk-${caseId}`,
    instrumentations: [new VercelAIInstrumentor()],
    traceContent: true,
    silenceInitializationMessage: true,
  });

  const telemetry = (scenario, metadata = {}) => ({
    functionId: `vercel_ai_sdk_${caseId}_${scenario}`,
    metadata: {
      run_id: runId,
      scenario,
      example: "vercel-ai-sdk",
      customer_params: JSON.stringify({
        customer_identifier: `customer-${runId}`,
        email: "vercel-ai-sdk@example.com",
        name: "Vercel AI SDK Example",
      }),
      thread_identifier: `thread-${runId}`,
      session_identifier: `session-${runId}`,
      trace_group_identifier: `trace-group-${runId}`,
      ...metadata,
    },
  });

  console.log(`run_id: ${runId}`);
  console.log(`model: ${modelName}`);
  console.log(`gateway_base_url: ${gatewayBaseURL}`);

  await respan.initialize();
  ensureTelemetryRegistered();
  try {
    await respan.withWorkflow(
      {
        name: `vercel_ai_sdk_${caseId}.workflow`,
        associationProperties: {
          run_id: runId,
          case_id: caseId,
          example: "vercel-ai-sdk",
        },
      },
      async () => await fn({ gateway, modelName, embeddingModelName, telemetry, runId }),
    );
  } finally {
    await respan.shutdown();
  }

  return runId;
}
