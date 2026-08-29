import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { VertexAIInstrumentor } from "@respan/instrumentation-vertexai";
import { Respan } from "@respan/respan";
import { FakeVertexAIModule, VertexAI as FakeVertexAI } from "./_fake_vertexai.js";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";
const DEFAULT_LOCATION = "us-central1";
const DEFAULT_MODEL = "gemini-2.0-flash";

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `vertexai-ts-${Date.now()}`;

let rootEnvLoaded = false;
let respanLogsSuppressed = false;
const originalConsoleDebug = console.debug.bind(console);
const originalConsoleInfo = console.info.bind(console);
const originalConsoleLog = console.log.bind(console);

export interface VertexExampleRuntime {
  mode: "fake" | "real";
  model: any;
  respan: Respan;
}

export interface VertexModelOptions {
  generationConfig?: Record<string, unknown>;
  model?: string;
  systemInstruction?: unknown;
  tools?: unknown[];
}

export const WEATHER_TOOL = {
  functionDeclarations: [
    {
      name: "lookup_weather",
      description: "Look up a compact weather summary for a city.",
      parameters: {
        type: "object",
        properties: {
          city: {
            type: "string",
            description: "City name",
          },
        },
        required: ["city"],
      },
    },
  ],
};

function suppressExampleRespanLogs(): void {
  if (respanLogsSuppressed || process.env.RESPAN_EXAMPLE_DEBUG === "true") {
    return;
  }

  console.debug = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]") || firstArg.startsWith("[Respan Debug]")) {
      return;
    }
    originalConsoleDebug(...args);
  };

  console.info = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]")) {
      return;
    }
    originalConsoleInfo(...args);
  };

  console.log = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]") || firstArg.startsWith("Respan tracing")) {
      return;
    }
    originalConsoleLog(...args);
  };

  respanLogsSuppressed = true;
}

export function loadRootEnv(): void {
  if (rootEnvLoaded) return;

  const startDir = dirname(fileURLToPath(import.meta.url));
  let currentDir = startDir;

  for (let depth = 0; depth < 8; depth += 1) {
    const envPath = join(currentDir, ".env");
    if (existsSync(envPath)) {
      dotenv.config({ path: envPath, override: false, quiet: true });
      rootEnvLoaded = true;
      return;
    }
    const parentDir = dirname(currentDir);
    if (parentDir === currentDir) break;
    currentDir = parentDir;
  }

  dotenv.config({ override: false, quiet: true });
  rootEnvLoaded = true;
}

function requireRespanApiKey(): string {
  const apiKey = process.env.RESPAN_API_KEY ?? process.env.RESPAN_GATEWAY_API_KEY;
  if (!apiKey) {
    throw new Error(
      "RESPAN_API_KEY or RESPAN_GATEWAY_API_KEY is required in respan-example-projects/.env.",
    );
  }
  return apiKey;
}

function respanBaseUrl(): string {
  return process.env.RESPAN_BASE_URL ?? process.env.RESPAN_GATEWAY_BASE_URL ?? DEFAULT_BASE_URL;
}

function googleProject(): string | undefined {
  return process.env.GOOGLE_CLOUD_PROJECT ??
    process.env.GOOGLE_VERTEXAI_PROJECT ??
    process.env.GCLOUD_PROJECT;
}

function googleLocation(): string {
  return process.env.GOOGLE_CLOUD_LOCATION ??
    process.env.GOOGLE_VERTEXAI_LOCATION ??
    DEFAULT_LOCATION;
}

function vertexModelName(model?: string): string {
  return model ??
    process.env.VERTEXAI_MODEL ??
    process.env.GOOGLE_VERTEXAI_MODEL ??
    DEFAULT_MODEL;
}

function shouldUseFakeVertex(): boolean {
  return process.env.VERTEXAI_EXAMPLE_MODE === "fake";
}

function requireGoogleProject(): string {
  const project = googleProject();
  if (!project) {
    throw new Error(
      "Google Vertex AI examples require GOOGLE_CLOUD_PROJECT or GOOGLE_VERTEXAI_PROJECT in respan-example-projects/.env. " +
        "Set VERTEXAI_EXAMPLE_MODE=fake only when you intentionally want the deterministic instrumentation smoke mode.",
    );
  }
  return project;
}

export async function createVertexExampleRuntime(
  appName: string,
  options: VertexModelOptions = {},
): Promise<VertexExampleRuntime> {
  loadRootEnv();
  suppressExampleRespanLogs();

  const modelName = vertexModelName(options.model);

  if (!shouldUseFakeVertex()) {
    const project = requireGoogleProject();
    const vertexModule = await import("@google-cloud/vertexai");
    const instrumentor = new VertexAIInstrumentor({ sdkModule: vertexModule as any });
    const respan = new Respan({
      apiKey: requireRespanApiKey(),
      baseURL: respanBaseUrl(),
      appName,
      instrumentations: [instrumentor],
      silenceInitializationMessage: true,
    });
    await respan.initialize();

    const vertexAI = new vertexModule.VertexAI({
      project,
      location: googleLocation(),
    });
    const model = vertexAI.getGenerativeModel({
      model: modelName,
      generationConfig: options.generationConfig,
      systemInstruction: options.systemInstruction,
      tools: options.tools,
    } as any);

    return { mode: "real", model, respan };
  }

  const instrumentor = new VertexAIInstrumentor({ sdkModule: FakeVertexAIModule as any });
  const respan = new Respan({
    apiKey: requireRespanApiKey(),
    baseURL: respanBaseUrl(),
    appName,
    instrumentations: [instrumentor],
    silenceInitializationMessage: true,
  });
  await respan.initialize();

  const vertexAI = new FakeVertexAI();
  const model = vertexAI.getGenerativeModel({
    model: modelName,
    generationConfig: options.generationConfig,
    systemInstruction: options.systemInstruction,
    tools: options.tools,
  });
  return { mode: "fake", model, respan };
}

export async function runWithExampleTrace<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  return await respan.propagateAttributes(
    {
      custom_identifier: EXAMPLE_RUN_ID,
      trace_group_identifier: workflowName,
      metadata: {
        example: "typescript-vertexai",
        run_id: EXAMPLE_RUN_ID,
        workflow_name: workflowName,
      },
    },
    () => respan.withWorkflow({ name: workflowName }, fn),
  );
}

export async function flushAndShutdown(
  respan: Pick<Respan, "shutdown">,
): Promise<void> {
  await respan.shutdown();
}

export function logExampleResult(
  workflowName: string,
  details: Record<string, unknown>,
): void {
  console.log(JSON.stringify({ workflowName, runId: EXAMPLE_RUN_ID, ...details }, null, 2));
}

export async function responseFromResult(result: any): Promise<any> {
  return await Promise.resolve(result?.response ?? result);
}

export function textFromResponse(response: any): string {
  const textProp = response?.text;
  if (typeof textProp === "string") return textProp;
  if (typeof textProp === "function") {
    try {
      const text = textProp.call(response);
      if (typeof text === "string") return text;
    } catch {
      // Fall back to candidates.
    }
  }
  return (response?.candidates ?? [])
    .flatMap((candidate: any) => candidate?.content?.parts ?? [])
    .map((part: any) => part?.text ?? "")
    .filter(Boolean)
    .join("");
}

export function functionCallsFromResponse(response: any): unknown[] {
  return (response?.candidates ?? [])
    .flatMap((candidate: any) => candidate?.content?.parts ?? [])
    .map((part: any) => part?.functionCall)
    .filter(Boolean);
}
