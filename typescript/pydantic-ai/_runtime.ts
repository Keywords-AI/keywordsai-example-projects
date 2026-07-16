import { trace } from "@opentelemetry/api";
import { PydanticAIInstrumentor } from "@respan/instrumentation-pydantic-ai";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import OpenAI from "openai";

const DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai";
const DEFAULT_GATEWAY_BASE_URL = "https://api.respan.ai/api";

let rootEnvLoaded = false;

export interface ExampleRuntime {
  client: OpenAI;
  respan: Respan;
  model: string;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
}

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `pydantic-ai-ts-${Date.now()}`;

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

export async function createRuntime(options: {
  appName: string;
  model: string;
}): Promise<ExampleRuntime> {
  loadRootEnv();
  const respanApiKey = requireEnv("RESPAN_API_KEY");
  const respanBaseURL = process.env.RESPAN_BASE_URL ?? DEFAULT_RESPAN_BASE_URL;
  const gatewayBaseURL =
    process.env.RESPAN_GATEWAY_BASE_URL ??
    process.env.OPENAI_BASE_URL ??
    DEFAULT_GATEWAY_BASE_URL;
  const gatewayApiKey = process.env.RESPAN_GATEWAY_API_KEY ?? respanApiKey;

  const respan = new Respan({
    apiKey: respanApiKey,
    baseURL: respanBaseURL,
    appName: options.appName,
    instrumentations: [new PydanticAIInstrumentor()],
    silenceInitializationMessage: true,
  });
  await respan.initialize();

  const client = new OpenAI({
    apiKey: gatewayApiKey,
    baseURL: gatewayBaseURL,
  });

  return { client, respan, model: options.model };
}

export async function runPydanticAIChat<T>(
  runtime: ExampleRuntime,
  options: {
    spanName: string;
    provider: string;
    messages: ChatMessage[];
    toolDefinitions?: unknown[];
    attributes?: Record<string, string | number | boolean>;
    fn: () => Promise<T>;
    outputMessages: (result: T) => ChatMessage[];
    usage?: (result: T) => {
      inputTokens?: number;
      outputTokens?: number;
      totalTokens?: number;
    };
  },
): Promise<T> {
  const tracer = trace.getTracer("pydantic-ai-compatible-example");
  const attributes: Record<string, string | number | boolean> = {
    "gen_ai.operation.name": "chat",
    "gen_ai.system": options.provider,
    "gen_ai.request.model": runtime.model,
    "gen_ai.input.messages": JSON.stringify(options.messages),
    ...options.attributes,
  };
  if (options.toolDefinitions) {
    attributes["gen_ai.tool.definitions"] = JSON.stringify(options.toolDefinitions);
  }

  return await runtime.respan.propagateAttributes(
    {
      custom_identifier: EXAMPLE_RUN_ID,
      trace_group_identifier: options.spanName,
      metadata: {
        example: "pydantic-ai-typescript",
        run_id: EXAMPLE_RUN_ID,
        provider: options.provider,
      },
    },
    async () =>
      await tracer.startActiveSpan(
        options.spanName,
        {
          attributes,
        },
        async (span) => {
          try {
            const result = await options.fn();
            span.setAttribute(
              "gen_ai.output.messages",
              JSON.stringify(options.outputMessages(result)),
            );
            const usage = options.usage?.(result);
            if (usage?.inputTokens !== undefined) {
              span.setAttribute("gen_ai.usage.input_tokens", usage.inputTokens);
            }
            if (usage?.outputTokens !== undefined) {
              span.setAttribute("gen_ai.usage.output_tokens", usage.outputTokens);
            }
            if (usage?.totalTokens !== undefined) {
              span.setAttribute("gen_ai.usage.total_tokens", usage.totalTokens);
            }
            return result;
          } finally {
            span.end();
          }
        },
      ),
  );
}

export async function runPydanticAITool<T>(
  toolName: string,
  args: Record<string, unknown>,
  fn: () => Promise<T>,
): Promise<T> {
  const tracer = trace.getTracer("pydantic-ai-compatible-example");
  return await tracer.startActiveSpan(
    `execute tool ${toolName}`,
    {
      attributes: {
        "gen_ai.tool.name": toolName,
        "gen_ai.tool.call.arguments": JSON.stringify(args),
      },
    },
    async (span) => {
      try {
        const result = await fn();
        span.setAttribute(
          "gen_ai.tool.call.result",
          typeof result === "string" ? result : JSON.stringify(result),
        );
        return result;
      } finally {
        span.end();
      }
    },
  );
}

export async function runPydanticAIAgent<T>(
  runtime: ExampleRuntime,
  options: {
    agentName: string;
    messages: ChatMessage[];
    toolDefinitions?: unknown[];
    fn: () => Promise<T>;
    finalResult: (result: T) => unknown;
  },
): Promise<T> {
  const tracer = trace.getTracer("pydantic-ai-compatible-example");
  const attributes: Record<string, string> = {
    "gen_ai.agent.name": options.agentName,
    "gen_ai.input.messages": JSON.stringify(options.messages),
  };
  if (options.toolDefinitions) {
    attributes["gen_ai.tool.definitions"] = JSON.stringify(options.toolDefinitions);
  }

  return await runtime.respan.propagateAttributes(
    {
      custom_identifier: EXAMPLE_RUN_ID,
      trace_group_identifier: options.agentName,
      metadata: {
        example: "pydantic-ai-typescript",
        run_id: EXAMPLE_RUN_ID,
        agent_name: options.agentName,
      },
    },
    async () =>
      await tracer.startActiveSpan(
        options.agentName,
        {
          attributes,
        },
        async (span) => {
          try {
            const result = await options.fn();
            span.setAttribute("final_result", JSON.stringify(options.finalResult(result)));
            return result;
          } finally {
            span.end();
          }
        },
      ),
  );
}

export async function runPydanticAIRunningTools<T>(
  toolNames: string[],
  fn: () => Promise<T>,
): Promise<T> {
  const tracer = trace.getTracer("pydantic-ai-compatible-example");
  return await tracer.startActiveSpan(
    "running tools",
    {
      attributes: {
        tools: JSON.stringify(toolNames),
      },
    },
    async (span) => {
      try {
        return await fn();
      } finally {
        span.end();
      }
    },
  );
}

export async function runPydanticAIOpenInference<T>(
  runtime: ExampleRuntime,
  options: {
    spanName: string;
    provider: string;
    input: string;
    fn: () => Promise<T>;
    output: (result: T) => string;
    usage?: (result: T) => {
      inputTokens?: number;
      outputTokens?: number;
      totalTokens?: number;
    };
  },
): Promise<T> {
  const tracer = trace.getTracer("@arizeai/openinference-instrumentation-pydantic-ai");
  return await runtime.respan.propagateAttributes(
    {
      custom_identifier: EXAMPLE_RUN_ID,
      trace_group_identifier: options.spanName,
      metadata: {
        example: "pydantic-ai-typescript",
        run_id: EXAMPLE_RUN_ID,
        provider: options.provider,
        span_style: "openinference",
      },
    },
    async () =>
      await tracer.startActiveSpan(
        options.spanName,
        {
          attributes: {
            "openinference.span.kind": "LLM",
            "input.value": options.input,
            "llm.model_name": runtime.model,
            "llm.provider": options.provider,
            "llm.input_messages.0.message.role": "user",
            "llm.input_messages.0.message.content": options.input,
          },
        },
        async (span) => {
          try {
            const result = await options.fn();
            const output = options.output(result);
            span.setAttribute("output.value", output);
            span.setAttribute("llm.output_messages.0.message.role", "assistant");
            span.setAttribute("llm.output_messages.0.message.content", output);
            const usage = options.usage?.(result);
            if (usage?.inputTokens !== undefined) {
              span.setAttribute("llm.token_count.prompt", usage.inputTokens);
            }
            if (usage?.outputTokens !== undefined) {
              span.setAttribute("llm.token_count.completion", usage.outputTokens);
            }
            if (usage?.totalTokens !== undefined) {
              span.setAttribute("llm.token_count.total", usage.totalTokens);
            }
            return result;
          } finally {
            span.end();
          }
        },
      ),
  );
}

export function firstText(response: OpenAI.Chat.Completions.ChatCompletion): string {
  return response.choices[0]?.message?.content ?? "";
}
