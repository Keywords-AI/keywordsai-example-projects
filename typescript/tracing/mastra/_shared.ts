import { createOpenAI } from "@ai-sdk/openai";
import type { Agent } from "@mastra/core/agent";
import { Mastra } from "@mastra/core/mastra";
import { SpanType } from "@mastra/core/observability";
import { Observability, SamplingStrategyType } from "@mastra/observability";
import { MastraInstrumentor } from "@respan/instrumentation-mastra";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `mastra-ts-${Date.now()}`;

let rootEnvLoaded = false;
let respanLogsSuppressed = false;
const originalConsoleDebug = console.debug.bind(console);
const originalConsoleInfo = console.info.bind(console);
const originalConsoleLog = console.log.bind(console);

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

export function createGatewayModel() {
  loadRootEnv();
  const respanApiKey = requireEnv("RESPAN_API_KEY");
  const baseURL = process.env.RESPAN_BASE_URL ?? DEFAULT_BASE_URL;

  process.env.OPENAI_API_KEY ||= respanApiKey;
  process.env.OPENAI_BASE_URL ||= baseURL;

  const openai = createOpenAI({
    apiKey: respanApiKey,
    baseURL,
  });

  return openai(process.env.MASTRA_EXAMPLE_MODEL ?? "gpt-4.1-nano");
}

export function createRuntime<TAgents extends Record<string, Agent<any>>>(
  agents: TAgents,
): { mastra: Mastra<TAgents>; respan: Respan; instrumentor: MastraInstrumentor } {
  loadRootEnv();
  suppressExampleRespanLogs();
  const instrumentor = new MastraInstrumentor();
  const respan = new Respan({
    apiKey: requireEnv("RESPAN_API_KEY"),
    baseURL: process.env.RESPAN_BASE_URL,
    appName: "mastra-typescript-examples",
    instrumentations: [instrumentor],
    silenceInitializationMessage: true,
  });

  const mastra = new Mastra({
    agents,
    observability: new Observability({
      configs: {
        default: {
          serviceName: "respan-mastra-typescript-examples",
          sampling: { type: SamplingStrategyType.ALWAYS },
          exporters: [instrumentor],
          excludeSpanTypes: [
            SpanType.MODEL_CHUNK,
            SpanType.MODEL_STEP,
            SpanType.MODEL_INFERENCE,
          ],
        },
      },
      sensitiveDataFilter: false,
    }),
  });

  return { mastra, respan, instrumentor };
}

export function getTraceWorkflowName(workflowName: string): string {
  return normalizeWorkflowName(workflowName).traceWorkflowName;
}

export async function runWithRespanWorkflow<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  const { mastraWorkflowName, traceWorkflowName } = normalizeWorkflowName(workflowName);
  await respan.initialize();
  try {
    return await respan.propagateAttributes(
      {
        custom_identifier: EXAMPLE_RUN_ID,
        trace_group_identifier: traceWorkflowName,
        metadata: {
          example: "mastra-typescript",
          run_id: EXAMPLE_RUN_ID,
          workflow_name: traceWorkflowName,
        },
      },
      () => respan.withWorkflow({ name: mastraWorkflowName }, fn),
    );
  } finally {
  }
}

function normalizeWorkflowName(workflowName: string): {
  mastraWorkflowName: string;
  traceWorkflowName: string;
} {
  const suffix = ".workflow";
  const mastraWorkflowName = workflowName.endsWith(suffix)
    ? workflowName.slice(0, -suffix.length)
    : workflowName;
  return {
    mastraWorkflowName,
    traceWorkflowName: `${mastraWorkflowName}${suffix}`,
  };
}
