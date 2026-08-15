import dotenv from "dotenv";
import * as LiveKit from "@livekit/agents";
import { Respan } from "@respan/respan";
import { LiveKitInstrumentor } from "@respan/instrumentation-livekit";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });
LiveKit.initializeLogger({ pretty: false, level: "silent" });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `livekit-ts-${Date.now()}`;

/** Stable model/provider labels keep example traces deterministic. */
export class ExampleFakeLLM extends LiveKit.voice.testing.FakeLLM {
  override get model(): string {
    return "livekit-fake-llm";
  }

  override get provider(): string {
    return "livekit";
  }
}

export function createRespan(appName: string): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [new LiveKitInstrumentor({ livekitModule: LiveKit })],
    silenceInitializationMessage: true,
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
        example: "typescript-livekit",
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

export async function closeSession(session: LiveKit.voice.AgentSession): Promise<void> {
  await session.close().catch(() => undefined);
}

export function summarizeRunEvents(result: LiveKit.voice.testing.RunResult): Array<Record<string, unknown>> {
  return result.events.map((event) => {
    if (event.type === "message") {
      return {
        type: event.type,
        role: event.item.role,
        text: event.item.textContent,
      };
    }
    if (event.type === "function_call") {
      return {
        type: event.type,
        name: event.item.name,
        args: event.item.args,
      };
    }
    if (event.type === "function_call_output") {
      return {
        type: event.type,
        name: event.item.name,
        output: event.item.output,
        isError: event.item.isError,
      };
    }
    return {
      type: event.type,
      newAgent: event.newAgent.id,
    };
  });
}
