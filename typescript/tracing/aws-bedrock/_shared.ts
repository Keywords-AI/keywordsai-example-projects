import {
  BedrockRuntimeClient,
  ConverseCommand,
  ConverseStreamCommand,
  InvokeModelCommand,
  InvokeModelWithResponseStreamCommand,
} from "@aws-sdk/client-bedrock-runtime";
import * as BedrockRuntimeModule from "@aws-sdk/client-bedrock-runtime";
import { AWSBedrockInstrumentor } from "@respan/instrumentation-aws-bedrock";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `aws-bedrock-ts-${Date.now()}`;
export const DEFAULT_CONVERSE_MODEL =
  process.env.AWS_BEDROCK_MODEL_ID || "anthropic.claude-3-haiku-20240307-v1:0";
export const DEFAULT_INVOKE_MODEL =
  process.env.AWS_BEDROCK_INVOKE_MODEL_ID || DEFAULT_CONVERSE_MODEL;

export interface BedrockLikeClient {
  send(command: unknown): Promise<any>;
}

function envValue(name: string): string | undefined {
  const direct = process.env[name];
  if (direct && direct.trim()) return direct.trim();
  const spaced = process.env[`${name} `];
  if (spaced && spaced.trim()) return spaced.trim();
  return undefined;
}

export function exampleMode(): "live" | "mock" {
  return process.env.AWS_BEDROCK_EXAMPLE_MODE === "live" ? "live" : "mock";
}

export function createRespan(appName = "aws-bedrock-typescript-examples"): Respan {
  const apiKey = envValue("RESPAN_API_KEY");
  if (!apiKey) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey,
    baseURL: envValue("RESPAN_BASE_URL"),
    appName,
    instrumentations: [
      exampleMode() === "live"
        ? new AWSBedrockInstrumentor({ sdkModule: BedrockRuntimeModule })
        : new AWSBedrockInstrumentor({ clientClass: MockBedrockRuntimeClient }),
    ],
    silenceInitializationMessage: true,
  });
}

export function createBedrockClient(): BedrockLikeClient {
  if (exampleMode() === "live") {
    return new BedrockRuntimeClient({
      region: envValue("AWS_REGION") || envValue("AWS_DEFAULT_REGION") || "us-east-1",
    });
  }
  return new MockBedrockRuntimeClient();
}

export async function runWithBedrockWorkflow<T>(
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
        example: "typescript-aws-bedrock",
        run_id: RUN_ID,
        workflow_name: workflowName,
        aws_bedrock_example_mode: exampleMode(),
      },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}

export async function shutdownRespan(respan: Respan): Promise<void> {
  await respan.shutdown();
}

export function logExampleResult(workflowName: string, details: Record<string, unknown>): void {
  console.log(JSON.stringify({ workflowName, runId: RUN_ID, mode: exampleMode(), ...details }, null, 2));
}

export async function withTimeout<T>(promise: Promise<T>, label: string): Promise<T> {
  let timeout: NodeJS.Timeout | undefined;
  const timeoutMs = Number.parseInt(process.env.AWS_BEDROCK_EXAMPLE_TIMEOUT_MS || "60000", 10);
  const timeoutPromise = new Promise<never>((_, reject) => {
    timeout = setTimeout(() => reject(new Error(`${label} timed out after ${timeoutMs}ms`)), timeoutMs);
  });
  try {
    return await Promise.race([promise, timeoutPromise]);
  } finally {
    if (timeout) clearTimeout(timeout);
  }
}

export function textFromConverseResponse(response: any): string {
  const content = response?.output?.message?.content;
  if (!Array.isArray(content)) return "";
  return content
    .map((block) => typeof block?.text === "string" ? block.text : "")
    .filter(Boolean)
    .join("\n");
}

export function decodeBody(body: unknown): string {
  if (body instanceof Uint8Array) {
    return new TextDecoder().decode(body);
  }
  if (typeof body === "string") {
    return body;
  }
  return JSON.stringify(body ?? null);
}

export async function collectConverseStreamText(stream: AsyncIterable<any>): Promise<string> {
  const parts: string[] = [];
  for await (const event of stream) {
    const text = event?.contentBlockDelta?.delta?.text;
    if (typeof text === "string") parts.push(text);
  }
  return parts.join("");
}

export async function collectInvokeStreamText(stream: AsyncIterable<any>): Promise<string> {
  const parts: string[] = [];
  for await (const event of stream) {
    const bytes = event?.chunk?.bytes;
    if (!(bytes instanceof Uint8Array)) continue;
    const payload = JSON.parse(new TextDecoder().decode(bytes));
    const text = payload?.delta?.text ?? payload?.completion ?? payload?.generation ?? payload?.outputText;
    if (typeof text === "string") parts.push(text);
  }
  return parts.join("");
}

function encodeJson(value: unknown): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(value));
}

function messageIncludes(input: any, text: string): boolean {
  const needle = text.toLowerCase();
  return (input?.messages || []).some((message: any) =>
    JSON.stringify(message).toLowerCase().includes(needle),
  );
}

export class MockBedrockRuntimeClient {
  async send(command: unknown): Promise<any> {
    const input = (command as any)?.input || {};

    if (command instanceof ConverseCommand) {
      if (messageIncludes(input, "expected error")) {
        const error = new Error("Deterministic Bedrock example error");
        (error as any).$metadata = { httpStatusCode: 429 };
        throw error;
      }
      return mockConverseResponse(input);
    }

    if (command instanceof InvokeModelCommand) {
      return mockInvokeModelResponse();
    }

    if (command instanceof ConverseStreamCommand) {
      return {
        $metadata: { httpStatusCode: 200 },
        stream: mockConverseStream(),
      };
    }

    if (command instanceof InvokeModelWithResponseStreamCommand) {
      return {
        $metadata: { httpStatusCode: 200 },
        body: mockInvokeModelStream(),
      };
    }

    return { $metadata: { httpStatusCode: 200 } };
  }
}

function mockConverseResponse(input: any): Record<string, unknown> {
  const hasTools = Array.isArray(input.toolConfig?.tools) && input.toolConfig.tools.length > 0;
  return {
    $metadata: { httpStatusCode: 200 },
    output: {
      message: {
        role: "assistant",
        content: hasTools
          ? [
              {
                toolUse: {
                  toolUseId: "toolu_city_weather",
                  name: "get_city_weather",
                  input: { city: "Tokyo" },
                },
              },
              { text: "Tokyo is clear and mild in the deterministic Bedrock example." },
            ]
          : [{ text: "Bedrock Converse instrumentation is active." }],
      },
    },
    usage: { inputTokens: 31, outputTokens: hasTools ? 18 : 7, totalTokens: hasTools ? 49 : 38 },
  };
}

function mockInvokeModelResponse(): Record<string, unknown> {
  return {
    $metadata: { httpStatusCode: 200 },
    body: encodeJson({
      content: [{ type: "text", text: "InvokeModel returned a deterministic Anthropic-style response." }],
      role: "assistant",
      usage: { input_tokens: 24, output_tokens: 9 },
    }),
  };
}

async function* mockConverseStream(): AsyncIterable<any> {
  yield {
    contentBlockStart: {
      start: {
        toolUse: {
          toolUseId: "toolu_stream_weather",
          name: "get_city_weather",
          input: { city: "Paris" },
        },
      },
    },
  };
  yield { contentBlockDelta: { delta: { text: "Paris" } } };
  yield { contentBlockDelta: { delta: { text: " stream response" } } };
  yield { metadata: { usage: { inputTokens: 18, outputTokens: 4, totalTokens: 22 } } };
}

async function* mockInvokeModelStream(): AsyncIterable<any> {
  yield {
    chunk: {
      bytes: encodeJson({ type: "content_block_delta", delta: { text: "Invoke" } }),
    },
  };
  yield {
    chunk: {
      bytes: encodeJson({ type: "content_block_delta", delta: { text: " stream" } }),
    },
  };
  yield {
    chunk: {
      bytes: encodeJson({ type: "message_delta", usage: { output_tokens: 2 } }),
    },
  };
}
