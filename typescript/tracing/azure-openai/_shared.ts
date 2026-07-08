import dotenv from "dotenv";
import * as OpenAIModule from "openai";
import { AzureOpenAI } from "openai";
import { Respan } from "@respan/respan";
import { AzureOpenAIInstrumentor } from "@respan/instrumentation-azure-openai";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `azure-openai-ts-${Date.now()}`;

type PatchRecord = {
  target: Record<string, any>;
  methodName: string;
  original: (...args: any[]) => any;
};

export function createRespan(appName: string): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [
      new AzureOpenAIInstrumentor({
        openAIModule: OpenAIModule,
      }),
    ],
    silenceInitializationMessage: true,
  });
}

export function createAzureClient(deployment = "gpt-4o-mini"): AzureOpenAI {
  return new AzureOpenAI({
    apiKey: process.env.AZURE_OPENAI_API_KEY || "azure-example-key",
    endpoint: process.env.AZURE_OPENAI_ENDPOINT || "https://respan-example.openai.azure.com",
    apiVersion: process.env.OPENAI_API_VERSION || "2024-10-21",
    deployment,
    maxRetries: 0,
  });
}

export async function runWithExampleTrace<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  return await respan.propagateAttributes(
    {
      trace_group_identifier: workflowName,
      custom_identifier: RUN_ID,
      metadata: {
        example: "typescript-azure-openai",
        run_id: RUN_ID,
        workflow_name: workflowName,
      },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}

export function logExampleResult(workflowName: string, details: Record<string, unknown>): void {
  console.log(JSON.stringify({ workflowName, runId: RUN_ID, ...details }, null, 2));
}

export function installMockAzureOpenAIResponses(): () => void {
  const patches: PatchRecord[] = [];

  patch(OpenAIModule.AzureOpenAI.Chat.Completions.prototype, "create", async (params: any) => {
    if (params.stream) {
      return streamChatCompletion(params.model || "gpt-4o-mini");
    }

    if (Array.isArray(params.messages) && params.messages.some((message: any) => message.role === "tool")) {
      return {
        id: "chatcmpl-respan-tool-answer",
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: params.model || "gpt-4o-mini",
        choices: [
          {
            index: 0,
            finish_reason: "stop",
            message: {
              role: "assistant",
              content: "Seattle has active waterfront neighborhoods and frequent ferry traffic.",
            },
          },
        ],
        usage: {
          prompt_tokens: 34,
          completion_tokens: 9,
          total_tokens: 43,
        },
      };
    }

    return {
      id: "chatcmpl-respan-demo",
      object: "chat.completion",
      created: Math.floor(Date.now() / 1000),
      model: params.model || "gpt-4o-mini",
      choices: [
        {
          index: 0,
          finish_reason: "stop",
          message: {
            role: "assistant",
            content: "Azure OpenAI tracing is active and exporting through Respan.",
          },
        },
      ],
      usage: {
        prompt_tokens: 18,
        completion_tokens: 11,
        total_tokens: 29,
      },
    };
  });

  patch(OpenAIModule.AzureOpenAI.Completions.prototype, "create", async (params: any) => ({
    id: "cmpl-respan-demo",
    object: "text_completion",
    created: Math.floor(Date.now() / 1000),
    model: params.model || "gpt-35-turbo-instruct",
    choices: [
      {
        index: 0,
        finish_reason: "stop",
        text: "Instrumented text completions are exported as Respan text spans.",
      },
    ],
    usage: {
      prompt_tokens: 9,
      completion_tokens: 10,
      total_tokens: 19,
    },
  }));

  patch(OpenAIModule.AzureOpenAI.Embeddings.prototype, "create", async (params: any) => ({
    object: "list",
    model: params.model || "text-embedding-3-small",
    data: [
      { object: "embedding", index: 0, embedding: [0.11, 0.22, 0.33] },
      { object: "embedding", index: 1, embedding: [0.44, 0.55, 0.66] },
    ],
    usage: {
      prompt_tokens: 7,
      total_tokens: 7,
    },
  }));

  function patch(
    target: Record<string, any>,
    methodName: string,
    replacement: (...args: any[]) => any,
  ): void {
    const original = target[methodName];
    patches.push({ target, methodName, original });
    target[methodName] = replacement;
  }

  return () => {
    for (const patchRecord of patches.reverse()) {
      patchRecord.target[patchRecord.methodName] = patchRecord.original;
    }
  };
}

async function* streamChatCompletion(model: string): AsyncIterable<any> {
  yield {
    id: "chatcmpl-respan-stream",
    object: "chat.completion.chunk",
    created: Math.floor(Date.now() / 1000),
    model,
    choices: [
      {
        index: 0,
        delta: {
          role: "assistant",
          content: "Looking up ",
          tool_calls: [
            {
              index: 0,
              id: "call_city",
              type: "function",
              function: {
                name: "lookup_city",
                arguments: "{\"city\"",
              },
            },
          ],
        },
        finish_reason: null,
      },
    ],
  };

  yield {
    id: "chatcmpl-respan-stream",
    object: "chat.completion.chunk",
    created: Math.floor(Date.now() / 1000),
    model,
    choices: [
      {
        index: 0,
        delta: {
          content: "city notes.",
          tool_calls: [
            {
              index: 0,
              function: {
                arguments: ":\"Seattle\"}",
              },
            },
          ],
        },
        finish_reason: "tool_calls",
      },
    ],
    usage: {
      prompt_tokens: 22,
      completion_tokens: 6,
      total_tokens: 28,
    },
  };
}
