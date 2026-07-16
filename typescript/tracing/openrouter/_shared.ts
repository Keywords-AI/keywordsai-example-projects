import dotenv from "dotenv";
import { OpenRouter } from "@openrouter/sdk";
import { HTTPClient } from "@openrouter/sdk/lib/http.js";
import { Respan } from "@respan/respan";
import { OpenRouterInstrumentor } from "@respan/instrumentation-openrouter";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `openrouter-ts-${Date.now()}`;
const USE_RESPAN_GATEWAY = !process.env.OPENROUTER_API_KEY && Boolean(process.env.RESPAN_GATEWAY_API_KEY || process.env.RESPAN_API_KEY);

export const CHAT_MODEL = process.env.OPENROUTER_CHAT_MODEL || process.env.RESPAN_MODEL || "openai/gpt-4o-mini";
export const EMBEDDING_MODEL = process.env.OPENROUTER_EMBEDDING_MODEL || (USE_RESPAN_GATEWAY ? "text-embedding-3-small" : "openai/text-embedding-3-small");
export const OPENROUTER_SERVER_URL = process.env.OPENROUTER_BASE_URL || (USE_RESPAN_GATEWAY ? process.env.RESPAN_GATEWAY_BASE_URL || process.env.RESPAN_BASE_URL : undefined);

export function createOpenRouterClient(): OpenRouter {
  const apiKey = process.env.OPENROUTER_API_KEY || process.env.RESPAN_GATEWAY_API_KEY || process.env.RESPAN_API_KEY;
  if (!apiKey) {
    throw new Error("Set OPENROUTER_API_KEY or RESPAN_GATEWAY_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new OpenRouter({
    apiKey,
    serverURL: OPENROUTER_SERVER_URL,
    httpClient: USE_RESPAN_GATEWAY ? createGatewayCompatibleHttpClient() : undefined,
    httpReferer: process.env.OPENROUTER_HTTP_REFERER || "https://respan.ai",
    appTitle: process.env.OPENROUTER_APP_TITLE || "Respan OpenRouter TypeScript examples",
  });
}

export function createRespan(appName = "openrouter-typescript-examples"): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [new OpenRouterInstrumentor()],
    silenceInitializationMessage: true,
  });
}

export async function runWithOpenRouterWorkflow<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  await respan.initialize();
  return await respan.propagateAttributes(
    {
      trace_group_identifier: workflowName,
      custom_identifier: RUN_ID,
      metadata: {
        example: "typescript-openrouter",
        run_id: RUN_ID,
        workflow_name: workflowName,
      },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}

export async function shutdownRespan(respan: Respan): Promise<void> {
  await respan.shutdown();
}

export function logExampleResult(workflowName: string, details: Record<string, unknown>): void {
  console.log(JSON.stringify({ workflowName, runId: RUN_ID, ...details }, null, 2));
}


function createGatewayCompatibleHttpClient(): HTTPClient {
  return new HTTPClient({
    fetcher: async (input, init) => {
      const response = await fetch(input, init);
      const contentType = response.headers.get("content-type") || "";
      if (!response.body || !contentType.includes("text/event-stream")) return response;

      const headers = new Headers(response.headers);
      headers.delete("content-length");
      return new Response(normalizeGatewaySse(response.body), {
        status: response.status,
        statusText: response.statusText,
        headers,
      });
    },
  });
}

function normalizeGatewaySse(body: ReadableStream<Uint8Array>): ReadableStream<Uint8Array> {
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();
  let buffered = "";
  let reader: ReadableStreamDefaultReader<Uint8Array>;

  return new ReadableStream<Uint8Array>({
    async start(controller) {
      reader = body.getReader();
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffered += decoder.decode(value, { stream: true });
          const events = buffered.split(/\r?\n\r?\n/);
          buffered = events.pop() || "";
          for (const event of events) controller.enqueue(encoder.encode(`${normalizeGatewaySseEvent(event)}\n\n`));
        }
        buffered += decoder.decode();
        if (buffered.trim()) controller.enqueue(encoder.encode(normalizeGatewaySseEvent(buffered)));
        controller.close();
      } catch (error) {
        controller.error(error);
      }
    },
    cancel(reason) {
      return reader?.cancel(reason);
    },
  });
}

function normalizeGatewaySseEvent(event: string): string {
  return event
    .split(/\r?\n/)
    .map((line) => {
      if (!line.startsWith("data:")) return line;
      const raw = line.slice(5).trim();
      if (!raw || raw === "[DONE]") return line;
      try {
        const payload = JSON.parse(raw);
        if (Array.isArray(payload.choices)) {
          for (const choice of payload.choices) {
            if (choice && choice.finish_reason === undefined) choice.finish_reason = "stop";
          }
        }
        return `data: ${JSON.stringify(payload)}`;
      } catch {
        return line;
      }
    })
    .join("\n");
}
