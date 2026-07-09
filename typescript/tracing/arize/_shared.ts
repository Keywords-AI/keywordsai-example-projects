import dotenv from "dotenv";
import { Respan } from "@respan/respan";
import { ArizeInstrumentor } from "@respan/instrumentation-arize";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `arize-ts-${Date.now()}`;

export function createRespan(appName = "arize-typescript-examples"): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [new ArizeInstrumentor()],
    silenceInitializationMessage: true,
  });
}

export async function runWithArizeWorkflow<T>(
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
        example: "typescript-arize",
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
