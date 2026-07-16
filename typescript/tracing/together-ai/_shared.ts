import dotenv from "dotenv";
import Together from "together-ai";
import { Respan } from "@respan/respan";
import { TogetherAIInstrumentor } from "@respan/instrumentation-together-ai";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `together-ai-ts-${Date.now()}`;
export const EXAMPLE_DIR = exampleDir;
const DEFAULT_TIMEOUT_SECONDS = Number.parseInt(
  process.env.TOGETHER_EXAMPLE_TIMEOUT_SECONDS || "180",
  10,
);

function envValue(name: string): string | undefined {
  const direct = process.env[name];
  if (direct && direct.trim()) return direct.trim();
  const spaced = process.env[`${name} `];
  if (spaced && spaced.trim()) return spaced.trim();
  return undefined;
}

export function createRespan(appName = "together-ai-typescript-examples"): Respan {
  const apiKey = envValue("RESPAN_API_KEY");
  if (!apiKey) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey,
    baseURL: envValue("RESPAN_BASE_URL"),
    appName,
    instrumentations: [new TogetherAIInstrumentor()],
    silenceInitializationMessage: true,
  });
}

export function createTogether(): Together {
  const apiKey = envValue("TOGETHER_API_KEY") || envValue("RESPAN_TOGETHER_API_KEY");
  if (!apiKey) {
    throw new Error("Set TOGETHER_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Together({
    apiKey,
    baseURL: envValue("TOGETHER_BASE_URL"),
    maxRetries: Number.parseInt(envValue("TOGETHER_MAX_RETRIES") || "1", 10),
  });
}

export const MODELS = {
  chat: envValue("TOGETHER_CHAT_MODEL") || envValue("TOGETHER_MODEL") || "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  completion: envValue("TOGETHER_COMPLETION_MODEL") || "mistralai/Mixtral-8x7B-Instruct-v0.1",
  embedding: envValue("TOGETHER_EMBEDDING_MODEL") || "togethercomputer/m2-bert-80M-8k-retrieval",
  image: envValue("TOGETHER_IMAGE_MODEL") || "black-forest-labs/FLUX.1-schnell-Free",
  rerank: envValue("TOGETHER_RERANK_MODEL") || "Salesforce/Llama-Rank-v1",
  speech: envValue("TOGETHER_SPEECH_MODEL") || "cartesia/sonic",
  speechVoice: envValue("TOGETHER_SPEECH_VOICE") || "friendly sidekick",
  transcription: envValue("TOGETHER_TRANSCRIPTION_MODEL") || "openai/whisper-large-v3",
};

export async function runWithTogetherWorkflow<T>(
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
        example: "typescript-together-ai",
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

export async function captureFeature<T>(
  label: string,
  run: () => Promise<T>,
): Promise<{ ok: true; value: T } | { ok: false; message: string; status?: number }> {
  try {
    return { ok: true, value: await withTimeout(run(), label) };
  } catch (error) {
    const record = error && typeof error === "object" ? error as Record<string, unknown> : {};
    const status = typeof record.status === "number" ? record.status : undefined;
    return {
      ok: false,
      message: error instanceof Error ? error.message : String(error),
      ...(status ? { status } : {}),
    };
  }
}

export async function withTogetherRetries<T>(
  label: string,
  run: () => Promise<T>,
  attempts = 2,
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await run();
    } catch (error) {
      lastError = error;
      if (attempt >= attempts || !isTransientTogetherError(error)) throw error;
      const delayMs = 1500 * attempt;
      console.warn(`${label}: transient Together AI error on attempt ${attempt}; retrying in ${delayMs}ms.`);
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  throw lastError instanceof Error ? lastError : new Error(String(lastError));
}

function isTransientTogetherError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return /temporar|429|500|502|503|504|rate limit|ECONNRESET|ETIMEDOUT/i.test(message);
}

export function summarizeChatCompletion(response: any): Record<string, unknown> {
  const choice = response?.choices?.[0];
  return {
    model: response?.model,
    content: choice?.message?.content ?? choice?.text ?? null,
    finishReason: choice?.finish_reason ?? null,
    toolCalls: choice?.message?.tool_calls?.length ?? 0,
    usage: response?.usage ?? null,
  };
}

export async function createDemoWav(): Promise<string> {
  const dir = path.join(exampleDir, ".generated");
  await fs.mkdir(dir, { recursive: true });
  const wavPath = path.join(dir, "together-demo.wav");
  const wavBase64 =
    "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=";
  await fs.writeFile(wavPath, Buffer.from(wavBase64, "base64"));
  return wavPath;
}
