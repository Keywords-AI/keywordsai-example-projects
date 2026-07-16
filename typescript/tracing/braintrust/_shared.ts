import { BraintrustInstrumentor } from "@respan/instrumentation-braintrust";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import OpenAI from "openai";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `braintrust-ts-${Date.now()}`;
export const EXAMPLE_MODEL =
  process.env.BRAINTRUST_EXAMPLE_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4.1-nano";

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

export function createOpenAIClient(): OpenAI {
  loadRootEnv();
  const respanApiKey = process.env.RESPAN_GATEWAY_API_KEY ?? requireEnv("RESPAN_API_KEY");
  const baseURL = process.env.RESPAN_GATEWAY_BASE_URL ?? process.env.RESPAN_BASE_URL ?? DEFAULT_BASE_URL;

  return new OpenAI({
    apiKey: respanApiKey,
    baseURL,
  });
}

export function createRuntime(): { respan: Respan; instrumentor: BraintrustInstrumentor } {
  loadRootEnv();
  suppressExampleRespanLogs();

  const instrumentor = new BraintrustInstrumentor();
  const respan = new Respan({
    apiKey: requireEnv("RESPAN_API_KEY"),
    baseURL: process.env.RESPAN_BASE_URL,
    appName: "braintrust-typescript-examples",
    instrumentations: [instrumentor],
    silenceInitializationMessage: true,
  });

  return { respan, instrumentor };
}

export async function runWithBraintrustWorkflow<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  const { entityWorkflowName, traceWorkflowName } = normalizeWorkflowName(workflowName);
  await respan.initialize();
  try {
    return await respan.propagateAttributes(
      {
        custom_identifier: EXAMPLE_RUN_ID,
        trace_group_identifier: traceWorkflowName,
        metadata: {
          example: "braintrust-typescript",
          run_id: EXAMPLE_RUN_ID,
          workflow_name: traceWorkflowName,
        },
      },
      () => respan.withWorkflow({ name: entityWorkflowName }, fn),
    );
  } finally {
  }
}

export function getTraceWorkflowName(workflowName: string): string {
  return normalizeWorkflowName(workflowName).traceWorkflowName;
}

export function logExampleResult(
  workflowName: string,
  details: Record<string, unknown>,
): void {
  console.log(JSON.stringify({
    workflowName: getTraceWorkflowName(workflowName),
    runId: EXAMPLE_RUN_ID,
    ...details,
  }, null, 2));
}

export function secondsAgo(offset: number): number {
  return Date.now() / 1000 - offset;
}

export function rowId(name: string): string {
  return `${EXAMPLE_RUN_ID}-${name}`;
}

function normalizeWorkflowName(workflowName: string): {
  entityWorkflowName: string;
  traceWorkflowName: string;
} {
  const suffix = ".workflow";
  const entityWorkflowName = workflowName.endsWith(suffix)
    ? workflowName.slice(0, -suffix.length)
    : workflowName;
  return {
    entityWorkflowName,
    traceWorkflowName: `${entityWorkflowName}${suffix}`,
  };
}
