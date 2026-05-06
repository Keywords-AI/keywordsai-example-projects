import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import { embed, embedMany, generateObject, generateText, streamObject, streamText, tool } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";
import { Respan } from "@respan/respan";
import { VercelAIInstrumentor } from "@respan/instrumentation-vercel";

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: resolve(__dirname, "../../../.env"), override: true });

const runId = `vercel-complex-${Date.now()}`;
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

const gateway = createOpenAI({
  apiKey: gatewayApiKey,
  baseURL: gatewayBaseUrl,
});

const respan = new Respan({
  apiKey: process.env.RESPAN_API_KEY,
  baseURL: respanBaseUrl,
  appName: "vercel-instrumentation-complex-live",
  instrumentations: [new VercelAIInstrumentor()],
  traceContent: true,
  silenceInitializationMessage: false,
});

const sleep = (ms) => new Promise((resolveSleep) => setTimeout(resolveSleep, ms));

const incidentLookup = tool({
  description: "Return nested incident metadata with unicode and arrays.",
  parameters: z.object({
    incidentId: z.string(),
    includeTimeline: z.boolean().default(true),
  }),
  execute: async ({ incidentId, includeTimeline }) => ({
    incidentId,
    severity: "p1",
    region: "iad1",
    summary: "Checkout latency spike with unicode payload: 東京 🌐",
    timeline: includeTimeline
      ? [
          { at: "2026-05-06T02:01:00Z", event: "alert_opened" },
          { at: "2026-05-06T02:04:00Z", event: "rollback_started" },
        ]
      : [],
    tags: ["vercel-ai-sdk", "complex-edge-case", runId],
  }),
});

const emptyNotes = tool({
  description: "Return an empty string to exercise blank tool outputs.",
  parameters: z.object({
    topic: z.string(),
  }),
  execute: async () => "",
});

const slowMetrics = tool({
  description: "Return service metrics after a short delay.",
  parameters: z.object({
    service: z.string(),
  }),
  execute: async ({ service }) => {
    await sleep(350);
    return {
      service,
      p50Ms: 121,
      p95Ms: 1840,
      sampleCount: 2048,
      runId,
    };
  },
});

function scenarioTelemetry(scenario, metadata = {}) {
  return {
    isEnabled: true,
    functionId: `vercel_complex_${scenario}_live`,
    metadata: {
      run_id: runId,
      scenario,
      customer_params: JSON.stringify({
        customer_identifier: `customer-${runId}`,
        email: "vercel-complex@example.com",
        name: "Vercel Complex Live",
      }),
      thread_identifier: `thread-${runId}`,
      trace_group_identifier: `trace-group-${runId}`,
      ...metadata,
    },
  };
}

async function runScenario(name, fn) {
  console.log(`\n--- ${name} ---`);
  try {
    await fn();
    console.log(`completed: ${name}`);
  } catch (error) {
    console.log(`failed: ${name}: ${error?.name || "Error"}: ${error?.message || error}`);
    throw error;
  }
}

async function scenarioComplexGenerateText() {
  const result = await generateText({
    model: gateway(modelName),
    system:
      "You are an incident commander. Use tools when helpful. Keep the final answer under 120 words.",
    prompt:
      `Run ${runId}: investigate incident inc_live_123. Include severity, region, and one mitigation.`,
    tools: {
      incidentLookup,
      emptyNotes,
      slowMetrics,
    },
    maxSteps: 4,
    experimental_telemetry: scenarioTelemetry("generate_text"),
  });

  console.log(`text chars: ${result.text.length}`);
  console.log(result.text.slice(0, 240));
}

async function scenarioStreamText() {
  const result = await streamText({
    model: gateway(modelName),
    prompt:
      `Run ${runId}: stream a terse status update with two bullets and mention 東京 once.`,
    experimental_telemetry: scenarioTelemetry("stream_text"),
  });

  let streamed = "";
  for await (const chunk of result.textStream) {
    streamed += chunk;
  }
  console.log(`stream chars: ${streamed.length}`);
  console.log(streamed.slice(0, 240));
}

async function scenarioGenerateObject() {
  const result = await generateObject({
    model: gateway(modelName),
    schema: z.object({
      severity: z.enum(["p0", "p1", "p2", "p3"]),
      region: z.string(),
      mitigation: z.string(),
    }),
    prompt:
      `Run ${runId}: return JSON for incident inc_live_123 with severity p1, region iad1, and a mitigation.`,
    experimental_telemetry: scenarioTelemetry("generate_object"),
  });

  console.log(`object severity: ${result.object.severity}`);
  console.log(JSON.stringify(result.object).slice(0, 240));
}

async function scenarioStreamObject() {
  const result = streamObject({
    model: gateway(modelName),
    schema: z.object({
      status: z.string(),
      region: z.string(),
      confidence: z.number(),
    }),
    prompt:
      `Run ${runId}: stream JSON with status stable, region iad1, and confidence 0.91.`,
    experimental_telemetry: scenarioTelemetry("stream_object"),
  });

  let latest = {};
  for await (const partial of result.partialObjectStream) {
    latest = partial;
  }
  console.log(`stream object keys: ${Object.keys(latest).join(",")}`);
  console.log(JSON.stringify(latest).slice(0, 240));
}

async function scenarioEmbed() {
  const result = await embed({
    model: gateway.embedding(embeddingModelName),
    value: `Run ${runId}: embed a single incident summary for Vercel telemetry.`,
    experimental_telemetry: scenarioTelemetry("embed"),
  });

  console.log(`embedding length: ${result.embedding.length}`);
}

async function scenarioEmbedMany() {
  const result = await embedMany({
    model: gateway.embedding(embeddingModelName),
    values: [
      `Run ${runId}: checkout latency`,
      `Run ${runId}: rollback mitigation`,
      `Run ${runId}: streaming telemetry`,
    ],
    experimental_telemetry: scenarioTelemetry("embed_many"),
  });

  console.log(`embedding count: ${result.embeddings.length}`);
}

async function scenarioRapidSequential() {
  for (let i = 0; i < 3; i += 1) {
    const result = await generateText({
      model: gateway(modelName),
      prompt: `Run ${runId}: reply with exactly one color for sequence ${i + 1}.`,
      experimental_telemetry: scenarioTelemetry("rapid_sequence", {
        sequence_index: String(i + 1),
      }),
    });
    console.log(`sequence ${i + 1}: ${result.text.trim()}`);
  }
}

async function main() {
  console.log("============================================================");
  console.log("Vercel AI SDK complex live instrumentation run");
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
        name: "vercel_complex_edge_cases_live.workflow",
        associationProperties: {
          run_id: runId,
          framework: "vercel-ai-sdk",
          instrumentation: "respan-instrumentation-vercel",
        },
      },
      async () => {
        await runScenario("embed", scenarioEmbed);
        await runScenario("embedMany", scenarioEmbedMany);
        await runScenario("generateObject", scenarioGenerateObject);
        await runScenario("streamObject", scenarioStreamObject);
        await runScenario("complex generateText with tools", scenarioComplexGenerateText);
        await runScenario("streamText", scenarioStreamText);
        await runScenario("rapid sequential generateText", scenarioRapidSequential);
      }
    );
  } finally {
    console.log("\nflushing traces...");
    await respan.shutdown();
  }

  console.log("============================================================");
  console.log("Live run complete.");
  console.log(`Find on Respan platform by run_id: ${runId}`);
  console.log(`Expected workflow span: vercel_complex_edge_cases_live.workflow`);
  console.log("Expected LLM log type: text/chat, not task");
  console.log("============================================================");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
