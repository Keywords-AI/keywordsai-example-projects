import { OpenAIProvider, Runner, withTrace } from "@openai/agents";
import { OpenAIAgentsInstrumentor } from "@respan/instrumentation-openai-agents";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai";
const DEFAULT_GATEWAY_BASE_URL = "https://api.respan.ai/api";

let envLoaded = false;

export interface Runtime {
  model: string;
  modelProvider: OpenAIProvider;
  respan: Respan;
  runner: Runner;
  runId: string;
}

export function loadEnv(): void {
  if (envLoaded) return;
  let current = dirname(fileURLToPath(import.meta.url));
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

export function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required. Add it to respan-example-projects/.env.`);
  }
  return value;
}

export async function createRuntime(appName: string): Promise<Runtime> {
  loadEnv();
  const respanApiKey = requireEnv("RESPAN_API_KEY");
  const gatewayApiKey = process.env.RESPAN_GATEWAY_API_KEY ?? respanApiKey;
  const respanBaseURL = process.env.RESPAN_BASE_URL ?? DEFAULT_RESPAN_BASE_URL;
  const gatewayBaseURL =
    process.env.RESPAN_GATEWAY_BASE_URL ??
    process.env.OPENAI_BASE_URL ??
    DEFAULT_GATEWAY_BASE_URL;
  const model = process.env.RESPAN_MODEL ?? "gpt-4o-mini";
  const runId =
    process.env.RESPAN_EXAMPLE_RUN_ID?.trim() || `openai-agents-ts-${Date.now()}`;

  const respan = new Respan({
    apiKey: respanApiKey,
    baseURL: respanBaseURL,
    appName,
    instrumentations: [new OpenAIAgentsInstrumentor()],
    traceContent: true,
    silenceInitializationMessage: true,
  });
  await respan.initialize();

  const modelProvider = new OpenAIProvider({
    apiKey: gatewayApiKey,
    baseURL: gatewayBaseURL,
    useResponses: false,
  });
  const runner = new Runner({ modelProvider });

  console.log(`run_id: ${runId}`);
  console.log(`model: ${model}`);
  console.log(`gateway_base_url: ${gatewayBaseURL}`);

  return { model, modelProvider, respan, runner, runId };
}

export async function shutdownRuntime(runtime: Runtime): Promise<void> {
  await runtime.modelProvider.close();
  await runtime.respan.shutdown();
}

export async function withExampleTrace<T>(
  runtime: Runtime,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  return await withTrace(
    workflowName,
    async () => await fn(),
    {
      groupId: runtime.runId,
      metadata: {
        run_id: runtime.runId,
        custom_identifier: runtime.runId,
        example: "openai-agents-sdk",
      },
    },
  );
}
