import type {
  BaseLlmConnection,
  Event,
  LlmRequest,
  LlmResponse,
  RunConfig,
} from "@google/adk";
import { GoogleADKInstrumentor } from "@respan/instrumentation-google-adk";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod/v4";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";

type GoogleADKModule = typeof import("@google/adk");
type LlmAgentInstance = InstanceType<GoogleADKModule["LlmAgent"]>;

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `google-adk-ts-${Date.now()}`;

let googleADKModulePromise: Promise<GoogleADKModule> | undefined;
let rootEnvLoaded = false;
let respanLogsSuppressed = false;
const originalConsoleDebug = console.debug.bind(console);
const originalConsoleInfo = console.info.bind(console);
const originalConsoleLog = console.log.bind(console);

export function loadRootEnv(): void {
  if (rootEnvLoaded) {
    return;
  }

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
    if (parentDir === currentDir) {
      break;
    }
    currentDir = parentDir;
  }

  dotenv.config({ override: false, quiet: true });
  rootEnvLoaded = true;
}

export function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required. Add it to respan-example-projects/.env.`);
  }
  return value;
}

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

async function loadGoogleADK(): Promise<GoogleADKModule> {
  googleADKModulePromise ??= import("@google/adk");
  return googleADKModulePromise;
}

export type DemoMode = "hello" | "tool" | "stream";

function createDeterministicLlm(adk: GoogleADKModule, mode: DemoMode) {
  class DeterministicADKLlm extends adk.BaseLlm {
    constructor() {
      super({ model: `respan-demo-${mode}-model` });
    }

    async *generateContentAsync(
      llmRequest: LlmRequest,
      stream = false,
      _abortSignal?: AbortSignal,
    ): AsyncGenerator<LlmResponse, void> {
      const hasToolResponse = llmRequest.contents.some((content) =>
        content.parts?.some((part) => part.functionResponse),
      );

      if (mode === "tool" && !hasToolResponse) {
        yield {
          content: {
            role: "model",
            parts: [
              {
                functionCall: {
                  name: "get_weather",
                  args: { city: "Tokyo" },
                },
              },
            ],
          },
          usageMetadata: {
            promptTokenCount: 18,
            candidatesTokenCount: 4,
            totalTokenCount: 22,
          },
        };
        return;
      }

      if (stream) {
        yield {
          content: { role: "model", parts: [{ text: "Streaming " }] },
          partial: true,
        };
        yield {
          content: { role: "model", parts: [{ text: "ADK telemetry " }] },
          partial: true,
        };
      }

      yield {
        content: {
          role: "model",
          parts: [{ text: finalText(llmRequest) }],
        },
        usageMetadata: {
          promptTokenCount: mode === "tool" ? 28 : 14,
          candidatesTokenCount: mode === "tool" ? 9 : 7,
          totalTokenCount: mode === "tool" ? 37 : 21,
        },
      };
    }

    async connect(_llmRequest: LlmRequest): Promise<BaseLlmConnection> {
      throw new Error("Live connections are not used by these examples.");
    }
  }

  function finalText(llmRequest: LlmRequest): string {
    if (mode === "tool") {
      const toolResponse = llmRequest.contents
        .flatMap((content) => content.parts ?? [])
        .map((part) => part.functionResponse?.response)
        .find((response) => response !== undefined);
      const forecast = isRecord(toolResponse) && typeof toolResponse.forecast === "string"
        ? toolResponse.forecast
        : "available";
      return `The Tokyo forecast is ${forecast}.`;
    }

    if (mode === "stream") {
      return "complete with propagated Respan attributes.";
    }

    return "Hello from Google ADK TypeScript instrumentation.";
  }

  return new DeterministicADKLlm();
}

function createWeatherTool(adk: GoogleADKModule) {
  return new adk.FunctionTool({
    name: "get_weather",
    description: "Return a short deterministic weather forecast.",
    parameters: z.object({
      city: z.string().describe("City name"),
    }),
    execute: ({ city }) => ({
      city,
      forecast: city === "Tokyo" ? "sunny with light wind" : "clear",
    }),
  });
}

function createAgent(adk: GoogleADKModule, mode: DemoMode): LlmAgentInstance {
  return new adk.LlmAgent({
    name: `${mode}_agent`,
    description: `Deterministic ${mode} Google ADK demo agent`,
    model: createDeterministicLlm(adk, mode),
    instruction: "Use concise responses. Call tools when needed.",
    tools: mode === "tool" ? [createWeatherTool(adk)] : [],
  });
}

export function createRespan(appName: string): Respan {
  loadRootEnv();
  suppressExampleRespanLogs();

  return new Respan({
    apiKey: requireEnv("RESPAN_API_KEY"),
    baseURL: process.env.RESPAN_BASE_URL ?? DEFAULT_BASE_URL,
    appName,
    instrumentations: [new GoogleADKInstrumentor()],
    silenceInitializationMessage: true,
  });
}

export async function runADKExample(params: {
  appName: string;
  workflowName: string;
  mode: DemoMode;
  prompt: string;
  runConfig?: RunConfig;
  streaming?: boolean;
}): Promise<{ events: Event[]; output: string; respan: Respan }> {
  const respan = createRespan(params.appName);
  const events: Event[] = [];
  let output = "";

  await respan.initialize();
  try {
    const adk = await loadGoogleADK();
    const runner = new adk.InMemoryRunner({
      appName: params.appName,
      agent: createAgent(adk, params.mode),
    });
    const runConfig = params.runConfig ?? (params.streaming
      ? { streamingMode: adk.StreamingMode.SSE }
      : undefined);

    await respan.propagateAttributes(
      {
        custom_identifier: EXAMPLE_RUN_ID,
        thread_identifier: `google-adk-ts-thread-${EXAMPLE_RUN_ID}`,
        trace_group_identifier: params.workflowName,
        metadata: {
          example: "google-adk-typescript",
          run_id: EXAMPLE_RUN_ID,
          workflow_name: params.workflowName,
        },
      },
      async () => {
        await respan.withWorkflow({ name: params.workflowName }, async () => {
          for await (const event of runner.runEphemeral({
            userId: "respan-example-user",
            newMessage: {
              role: "user",
              parts: [{ text: params.prompt }],
            },
            runConfig,
          })) {
            events.push(event);
            output += stringifyEventText(event);
          }
        });
      },
    );
  } finally {
  }

  return { events, output, respan };
}

export function logExampleResult(
  workflowName: string,
  details: Record<string, unknown>,
): void {
  console.log(JSON.stringify({ workflowName, runId: EXAMPLE_RUN_ID, ...details }, null, 2));
}

function stringifyEventText(event: Event): string {
  return (event.content?.parts ?? [])
    .map((part) => part.text ?? "")
    .filter(Boolean)
    .join("");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
