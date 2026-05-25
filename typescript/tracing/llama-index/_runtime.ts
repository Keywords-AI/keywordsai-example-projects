import dotenv from "dotenv";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { OpenAI } from "@llamaindex/openai";
import { Respan } from "@respan/respan";
import { LlamaIndexInstrumentor } from "@respan/instrumentation-llama-index";
import * as LlamaIndex from "llamaindex";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT_ENV = path.resolve(__dirname, "../../../.env");

dotenv.config({ path: REPO_ROOT_ENV });

export const DEFAULT_MODEL = process.env.LLAMA_INDEX_TS_MODEL ?? "gpt-4.1-nano";

function createGatewayBaseURL(): string {
  const respanBaseUrl = (
    process.env.RESPAN_BASE_URL ?? "https://api.respan.ai"
  ).replace(/\/+$/, "");

  return respanBaseUrl.endsWith("/api")
    ? `${respanBaseUrl}/`
    : `${respanBaseUrl}/api/`;
}

export function createOpenAI(init: Partial<OpenAI> = {}): OpenAI {
  const useGateway = process.env.LLAMA_INDEX_USE_OPENAI_DIRECT !== "true";
  const gatewayBaseUrl = createGatewayBaseURL();

  const apiKey = useGateway
    ? process.env.RESPAN_API_KEY
    : process.env.OPENAI_API_KEY;

  if (!apiKey) {
    throw new Error(
      "Set RESPAN_API_KEY for gateway calls, or set LLAMA_INDEX_USE_OPENAI_DIRECT=true with OPENAI_API_KEY.",
    );
  }

  return new OpenAI({
    model: DEFAULT_MODEL,
    apiKey,
    baseURL: useGateway ? gatewayBaseUrl : process.env.OPENAI_BASE_URL,
    ...(init as Record<string, unknown>),
  });
}

export async function runNamedWorkflow<T>(
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the repository root .env.");
  }

  const respan = new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName: workflowName,
    traceContent: true,
    silenceInitializationMessage: true,
    instrumentations: [
      new LlamaIndexInstrumentor({
        workflowName,
        llamaIndexModule: LlamaIndex,
      }),
    ],
  });

  await respan.initialize();
  try {
    return await respan.propagateAttributes(
      {
        trace_group_identifier: workflowName,
        metadata: {
          example_set: "typescript/tracing/llama-index",
          workflow_name: workflowName,
        },
      },
      () =>
        respan.withWorkflow(
          {
            name: workflowName,
            associationProperties: {
              example_set: "typescript/tracing/llama-index",
              framework: "llama-index",
              language: "typescript",
            },
          },
          fn,
        ),
    );
  } finally {
    await respan.shutdown();
  }
}
