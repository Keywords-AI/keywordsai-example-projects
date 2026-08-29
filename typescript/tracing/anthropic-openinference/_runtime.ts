import dotenv from "dotenv";
import Anthropic from "@anthropic-ai/sdk";
import { AnthropicInstrumentation } from "@arizeai/openinference-instrumentation-anthropic";
import { Respan } from "@respan/respan";
import { OpenInferenceInstrumentor } from "@respan/instrumentation-openinference";
import { fileURLToPath } from "node:url";

dotenv.config({
  path: fileURLToPath(new URL("../../../.env", import.meta.url)),
  quiet: true,
});

export const RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID || `openinference-anthropic-${Date.now()}`;

function required(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Set ${name} in the repository-root .env file.`);
  return value;
}

export function createRuntime(): { respan: Respan } {
  return {
    respan: new Respan({
      apiKey: required("RESPAN_API_KEY"),
      baseURL: process.env.RESPAN_BASE_URL,
      instrumentations: [
        new OpenInferenceInstrumentor(AnthropicInstrumentation, Anthropic),
      ],
      silenceInitializationMessage: true,
    }),
  };
}

export function createAnthropicClient(): Anthropic {
  const gatewayBase = (
    process.env.RESPAN_GATEWAY_BASE_URL?.trim() || required("RESPAN_BASE_URL")
  ).replace(/\/$/, "");
  return new Anthropic({
    apiKey: process.env.RESPAN_GATEWAY_API_KEY?.trim() || required("RESPAN_API_KEY"),
    baseURL: `${gatewayBase}/anthropic`,
  });
}

export async function runWithOpenInferenceWorkflow<T>(
  respan: Respan,
  workflowName: string,
  fn: () => Promise<T>,
): Promise<T> {
  await respan.initialize();
  return await respan.propagateAttributes(
    {
      custom_identifier: RUN_ID,
      trace_group_identifier: workflowName,
      metadata: {
        example: "typescript-anthropic-openinference",
        run_id: RUN_ID,
        workflow_name: workflowName,
      },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}
