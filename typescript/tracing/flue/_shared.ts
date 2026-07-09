import * as FlueRuntime from "@flue/runtime";
import { createFlueContext, resolveModel } from "@flue/runtime/internal";
import { FlueInstrumentor } from "@respan/instrumentation-flue";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `flue-ts-${Date.now()}`;

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

export function createRuntime(workflowName: string): { respan: Respan; instrumentor: FlueInstrumentor } {
  loadRootEnv();
  suppressExampleRespanLogs();

  const instrumentor = new FlueInstrumentor({
    runtimeModule: FlueRuntime,
    workflowName: getTraceWorkflowName(workflowName),
  });
  const respan = new Respan({
    apiKey: requireEnv("RESPAN_API_KEY"),
    baseURL: process.env.RESPAN_BASE_URL ?? DEFAULT_BASE_URL,
    appName: "flue-typescript-examples",
    instrumentations: [instrumentor],
    silenceInitializationMessage: true,
  });

  return { respan, instrumentor };
}

export async function runWithFlueTrace<T>(
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
          example: "flue-typescript",
          run_id: EXAMPLE_RUN_ID,
          workflow_name: traceWorkflowName,
        },
      },
      () => respan.withWorkflow({ name: entityWorkflowName }, fn),
    );
  } finally {
    await respan.flush();
  }
}

export function createWorkflowContext(workflowName: string, payload: unknown) {
  return createFlueContext({
    id: `${EXAMPLE_RUN_ID}-${slug(workflowName)}`,
    runId: `${EXAMPLE_RUN_ID}-${slug(workflowName)}-run`,
    payload,
    env: process.env,
    agentConfig: { resolveModel },
    createDefaultEnv: async () => createNoopSessionEnv(),
    defaultStore: {} as any,
  });
}

export function createAgentContext(instanceName: string, input: unknown) {
  return createFlueContext({
    id: `${EXAMPLE_RUN_ID}-${slug(instanceName)}`,
    dispatchId: `${EXAMPLE_RUN_ID}-${slug(instanceName)}-dispatch`,
    payload: input,
    env: process.env,
    agentConfig: { resolveModel },
    createDefaultEnv: async () => createNoopSessionEnv(),
    defaultStore: {} as any,
  });
}

export function emit(ctx: ReturnType<typeof createFlueContext>, event: Record<string, unknown>) {
  return ctx.emitEvent(event as any);
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

function slug(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function createNoopSessionEnv() {
  return {
    cwd: "/workspace",
    resolvePath(path: string) {
      return path.startsWith("/") ? path : `/workspace/${path}`;
    },
    async exec(command: string) {
      return { stdout: `noop: ${command}`, stderr: "", exitCode: 0 };
    },
    async readFile() {
      return "";
    },
    async readFileBuffer() {
      return new Uint8Array();
    },
    async writeFile() {},
    async stat() {
      return { isFile: true, isDirectory: false };
    },
    async readdir() {
      return [];
    },
    async exists() {
      return false;
    },
    async mkdir() {},
    async rm() {},
  };
}
