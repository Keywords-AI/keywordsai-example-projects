import Anthropic from "@anthropic-ai/sdk";
import { AnthropicInstrumentor } from "@respan/instrumentation-anthropic";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { fileURLToPath } from "node:url";

dotenv.config({
  path: fileURLToPath(new URL("../../../.env", import.meta.url)),
  quiet: true,
});

export const RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID || `typescript-anthropic-${Date.now()}`;
export const MODEL =
  process.env.RESPAN_ANTHROPIC_MODEL?.trim() || "claude-sonnet-4-5-20250929";

function required(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Set ${name} in the repository-root .env file.`);
  return value;
}

export function createRuntime(): { client: Anthropic; respan: Respan } {
  const apiKey = required("RESPAN_API_KEY");
  const baseURL = required("RESPAN_BASE_URL").replace(/\/$/, "");
  return {
    client: new Anthropic({ apiKey, baseURL: `${baseURL}/anthropic` }),
    respan: new Respan({
      apiKey,
      baseURL,
      instrumentations: [new AnthropicInstrumentor()],
      silenceInitializationMessage: true,
    }),
  };
}

export async function runCase<T>(
  respan: Respan,
  caseId: string,
  fn: () => Promise<T>,
): Promise<T> {
  await respan.initialize();
  return await respan.propagateAttributes(
    {
      custom_identifier: `${RUN_ID}-${caseId}`,
      trace_group_identifier: RUN_ID,
      metadata: {
        example: "typescript-anthropic-direct",
        run_id: RUN_ID,
        case_id: caseId,
      },
    },
    async () => await respan.withWorkflow({ name: `anthropic_${caseId}` }, fn),
  );
}
