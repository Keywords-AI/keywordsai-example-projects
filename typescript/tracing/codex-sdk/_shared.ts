import dotenv from "dotenv";
import { Codex, type ThreadOptions } from "@openai/codex-sdk";
import * as CodexSDKModule from "@openai/codex-sdk";
import { Respan } from "@respan/respan";
import { CodexSDKInstrumentor } from "@respan/instrumentation-codex-sdk";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `codex-sdk-ts-${Date.now()}`;
export const EXAMPLE_DIR = exampleDir;
const DEFAULT_TIMEOUT_SECONDS = Number.parseInt(
  process.env.CODEX_EXAMPLE_TIMEOUT_SECONDS || "180",
  10,
);

function envValue(name: string): string | undefined {
  const direct = process.env[name];
  if (direct && direct.trim()) return direct.trim();
  const spaced = process.env[`${name} `];
  if (spaced && spaced.trim()) return spaced.trim();
  return undefined;
}

export function createRespan(appName = "codex-sdk-typescript-examples"): Respan {
  const apiKey = envValue("RESPAN_API_KEY");
  if (!apiKey) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey,
    baseURL: envValue("RESPAN_BASE_URL"),
    appName,
    instrumentations: [
      new CodexSDKInstrumentor({
        sdkModule: CodexSDKModule,
        workflowName: appName,
        agentName: "respan-codex-sdk-example-agent",
      }),
    ],
    silenceInitializationMessage: true,
  });
}

export function createCodex(options: { codexPathOverride?: string } = {}): Codex {
  const apiKey = envValue("CODEX_API_KEY") || envValue("RESPAN_GATEWAY_API_KEY") || envValue("OPENAI_API_KEY");
  if (!apiKey && !options.codexPathOverride) {
    throw new Error("Set CODEX_API_KEY, RESPAN_GATEWAY_API_KEY, or OPENAI_API_KEY in the repo root .env file.");
  }

  const env: Record<string, string> = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (typeof value === "string") env[key] = value;
  }
  if (apiKey) {
    env.CODEX_API_KEY = apiKey;
    env.OPENAI_API_KEY = apiKey;
  }

  return new Codex({
    apiKey,
    baseUrl: envValue("CODEX_BASE_URL") || envValue("RESPAN_GATEWAY_BASE_URL") || envValue("OPENAI_BASE_URL"),
    codexPathOverride: options.codexPathOverride,
    env,
  });
}

export function codexThreadOptions(overrides: ThreadOptions = {}): ThreadOptions {
  const model = envValue("CODEX_MODEL") || envValue("RESPAN_CODEX_MODEL");
  return {
    workingDirectory: EXAMPLE_DIR,
    skipGitRepoCheck: true,
    sandboxMode: "read-only",
    approvalPolicy: "never",
    networkAccessEnabled: false,
    webSearchEnabled: false,
    ...(model ? { model } : {}),
    ...overrides,
  };
}

export async function runWithCodexWorkflow<T>(
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
        example: "typescript-codex-sdk",
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

export async function withTimeout<T>(promise: Promise<T>, label: string): Promise<T> {
  let timeout: NodeJS.Timeout | undefined;
  const timeoutPromise = new Promise<never>((_, reject) => {
    timeout = setTimeout(
      () => reject(new Error(`${label} timed out after ${DEFAULT_TIMEOUT_SECONDS}s`)),
      DEFAULT_TIMEOUT_SECONDS * 1000,
    );
  });
  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    if (timeout) clearTimeout(timeout);
  }
}

export async function withCodexRetries<T>(
  label: string,
  run: () => Promise<T>,
  attempts = 3,
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await run();
    } catch (error) {
      lastError = error;
      if (attempt >= attempts || !isTransientCodexError(error)) {
        throw error;
      }
      const delayMs = 1500 * attempt;
      console.warn(`${label}: transient Codex error on attempt ${attempt}; retrying in ${delayMs}ms.`);
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  throw lastError instanceof Error ? lastError : new Error(String(lastError));
}

function isTransientCodexError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return /high demand|temporar|429|500|502|503|504|rate limit|ECONNRESET|ETIMEDOUT/i.test(message);
}

export async function createScratchWorkspace(name: string): Promise<string> {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), `${RUN_ID}-${name}-`));
  await fs.writeFile(path.join(dir, "README.md"), "# Codex SDK scratch workspace\n", "utf8");
  return dir;
}

export async function createDemoImage(): Promise<string> {
  const dir = path.join(exampleDir, ".generated");
  await fs.mkdir(dir, { recursive: true });
  const imagePath = path.join(dir, "codex-demo.png");
  const pngBase64 =
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAGElEQVR4nGP8z8DwnwEJMDIwMDAwAADpVgQDAZQcFwAAAABJRU5ErkJggg==";
  await fs.writeFile(imagePath, Buffer.from(pngBase64, "base64"));
  return imagePath;
}
