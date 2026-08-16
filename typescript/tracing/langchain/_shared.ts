import { Document } from "@langchain/core/documents";
import { BaseRetriever } from "@langchain/core/retrievers";
import type { RunnableConfig } from "@langchain/core/runnables";
import { FakeLLM, FakeListChatModel } from "@langchain/core/utils/testing";
import { LangChainInstrumentor } from "@respan/instrumentation-langchain";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { fileURLToPath } from "node:url";
import { tool } from "langchain";
import { z } from "zod";

dotenv.config({
  path: fileURLToPath(new URL("../../../.env", import.meta.url)),
  quiet: true,
});

export interface ExampleRuntime {
  enabled: boolean;
  instrumentor?: LangChainInstrumentor;
  respan?: Respan;
}

export async function initRespan(appName: string): Promise<ExampleRuntime> {
  const apiKey = process.env.RESPAN_API_KEY;
  if (!apiKey) {
    console.log("RESPAN_API_KEY is not set; running locally without exporting spans.");
    return { enabled: false };
  }

  const instrumentor = new LangChainInstrumentor();
  const respan = new Respan({
    apiKey,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [instrumentor],
    logLevel: "error",
    silenceInitializationMessage: true,
  });
  await respan.initialize();
  return { enabled: true, instrumentor, respan };
}

export function tracingConfig(
  runtime: ExampleRuntime,
  name: string,
  metadata: Record<string, unknown> = {},
): RunnableConfig {
  const config: RunnableConfig = {
    runName: name,
    tags: ["respan-langchain-example", name],
    metadata: {
      example: name,
      custom_identifier: process.env.RESPAN_EXAMPLE_RUN_ID,
      ...metadata,
    },
  };
  return runtime.instrumentor ? runtime.instrumentor.addCallback(config) : config;
}

export async function shutdown(runtime: ExampleRuntime): Promise<void> {
  await runtime.respan?.shutdown().catch(() => undefined);
}

export function fakeChat(responses: string[]): FakeListChatModel {
  return new FakeListChatModel({ responses });
}

export function fakeLlm(response: string): FakeLLM {
  return new FakeLLM({ response });
}

export function messageText(value: unknown): string {
  if (typeof value === "string") return value;
  if (value && typeof value === "object" && "content" in value) {
    const content = (value as { content: unknown }).content;
    return typeof content === "string" ? content : JSON.stringify(content);
  }
  return JSON.stringify(value);
}

export const getWeather = tool(
  ({ city }: { city: string }) => `It is sunny in ${city}.`,
  {
    name: "get_weather",
    description: "Get deterministic weather for a city.",
    schema: z.object({
      city: z.string().describe("City name"),
    }),
  },
);

export const addNumbers = tool(
  ({ left, right }: { left: number; right: number }) => left + right,
  {
    name: "add_numbers",
    description: "Add two numbers.",
    schema: z.object({
      left: z.number(),
      right: z.number(),
    }),
  },
);

export class StaticRetriever extends BaseRetriever {
  lc_namespace = ["respan", "examples", "langchain"];

  async _getRelevantDocuments(query: string): Promise<Document[]> {
    return [
      new Document({
        pageContent: `Respan tracing captures LangChain callbacks for ${query}.`,
        metadata: { source: "static-retriever" },
      }),
    ];
  }
}
