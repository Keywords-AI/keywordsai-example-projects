import dotenv from "dotenv";
import { Respan } from "@respan/respan";
import { SuperagentInstrumentor } from "@respan/instrumentation-superagent";
import type { SafetyClient, SupportedModel } from "safety-agent";
import type * as SafetyAgentModule from "safety-agent";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID || `superagent-ts-${Date.now()}`;

export interface ExampleConfig {
  respanApiKey: string;
  respanBaseURL?: string;
  model: SupportedModel;
}

export function configureEnvironment(): ExampleConfig {
  const respanApiKey = process.env.RESPAN_API_KEY;
  if (!respanApiKey) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  const respanBaseURL = process.env.RESPAN_BASE_URL;
  const gatewayApiKey = process.env.RESPAN_GATEWAY_API_KEY || respanApiKey;
  const gatewayBaseURL =
    process.env.RESPAN_GATEWAY_BASE_URL ||
    respanBaseURL ||
    "https://api.respan.ai/api";

  process.env.SUPERAGENT_API_KEY ||= "respan-superagent-example";
  process.env.OPENAI_COMPATIBLE_API_KEY = gatewayApiKey;
  process.env.OPENAI_COMPATIBLE_BASE_URL = gatewayBaseURL;
  process.env.OPENAI_COMPATIBLE_SUPPORTS_STRUCTURED_OUTPUT = "true";

  const rawModel = process.env.SUPERAGENT_MODEL || "gpt-4o-mini";
  const model = (rawModel.includes("/")
    ? rawModel
    : `openai-compatible/${rawModel}`) as SupportedModel;

  return {
    respanApiKey,
    respanBaseURL,
    model,
  };
}

let safetyAgentModulePromise: Promise<typeof SafetyAgentModule> | undefined;

async function loadSafetyAgentModule(): Promise<typeof SafetyAgentModule> {
  configureEnvironment();
  safetyAgentModulePromise ??= import("safety-agent");
  return await safetyAgentModulePromise;
}

export async function createRespan(appName: string): Promise<Respan> {
  const config = configureEnvironment();
  const safetyAgentModule = await loadSafetyAgentModule();

  return new Respan({
    apiKey: config.respanApiKey,
    baseURL: config.respanBaseURL,
    appName,
    instrumentations: [new SuperagentInstrumentor({ safetyAgentModule })],
    silenceInitializationMessage: true,
  });
}

export async function createSuperagentClient(): Promise<SafetyClient> {
  const { createClient } = await loadSafetyAgentModule();
  return createClient({
    apiKey: process.env.SUPERAGENT_API_KEY,
  });
}

export async function runWithExampleTrace<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  return await respan.propagateAttributes(
    {
      trace_group_identifier: workflowName,
      custom_identifier: RUN_ID,
      customer_identifier: "superagent-typescript-example-user",
      thread_identifier: `superagent-typescript-example-thread-${RUN_ID}`,
      metadata: {
        example: "typescript-superagent",
        run_id: RUN_ID,
        workflow_name: workflowName,
      },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}

export function logExampleResult(
  workflowName: string,
  details: Record<string, unknown>,
): void {
  console.log(JSON.stringify({ workflowName, runId: RUN_ID, ...details }, null, 2));
}
