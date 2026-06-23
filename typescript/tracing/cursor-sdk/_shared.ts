import dotenv from "dotenv";
import { Respan } from "@respan/respan";
import { CursorSDKInstrumentor } from "@respan/instrumentation-cursor";
import path from "node:path";
import { fileURLToPath } from "node:url";

type AnyRecord = Record<string, any>;

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `cursor-sdk-ts-${Date.now()}`;

export function createRespan(appName: string, sdkModule: AnyRecord): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }
  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [new CursorSDKInstrumentor({ sdkModule, agentName: appName })],
    silenceInitializationMessage: true,
  });
}

export async function runWithExampleTrace<T>(respan: Respan, workflowName: string, fn: () => Promise<T>): Promise<T> {
  return await respan.propagateAttributes(
    {
      trace_group_identifier: workflowName,
      custom_identifier: RUN_ID,
      metadata: { example: "typescript-cursor-sdk", run_id: RUN_ID, workflow_name: workflowName },
    },
    async () => await respan.withWorkflow({ name: workflowName }, fn),
  );
}

export function logExampleResult(workflowName: string, details: Record<string, unknown>): void {
  console.log(JSON.stringify({ workflowName, runId: RUN_ID, ...details }, null, 2));
}

export function createDemoCursorSDKModule(): AnyRecord {
  class DemoRun {
    readonly id: string;
    readonly requestId: string;
    readonly agentId: string;
    readonly model: { id: string };
    readonly result?: string;
    readonly durationMs?: number;
    readonly status = "running";
    private readonly messages: AnyRecord[];
    private readonly finalResult: string;

    constructor({ agentId, finalResult, messages, model, runId }: { agentId: string; finalResult: string; messages: AnyRecord[]; model: string; runId: string }) {
      this.agentId = agentId;
      this.finalResult = finalResult;
      this.id = runId;
      this.messages = messages;
      this.model = { id: model };
      this.requestId = `${runId}-request`;
    }

    supports(): boolean { return true; }
    unsupportedReason(): undefined { return undefined; }

    async *stream(): AsyncGenerator<AnyRecord, void> {
      for (const message of this.messages) {
        await new Promise((resolve) => setTimeout(resolve, 5));
        yield message;
      }
    }

    async wait(): Promise<AnyRecord> {
      return { id: this.id, requestId: this.requestId, status: "finished", result: this.finalResult, model: this.model, durationMs: 42 };
    }

    async conversation(): Promise<AnyRecord[]> { return []; }
    async cancel(): Promise<void> {}
    onDidChangeStatus(): () => void { return () => undefined; }
  }

  class DemoAgent {
    readonly agentId: string;
    readonly model: { id: string };
    private readonly name: string;

    constructor(options: AnyRecord = {}) {
      this.agentId = options.agentId ?? `agent_${Math.random().toString(16).slice(2, 10)}`;
      this.model = options.model ?? { id: "cursor-small" };
      this.name = options.name ?? "demo-cursor-agent";
    }

    async send(message: string | AnyRecord, options: AnyRecord = {}): Promise<DemoRun> {
      await options.onStep?.({ step: { type: "planning", summary: "Prepare the Cursor SDK example response." } });
      await options.onDelta?.({ update: { type: "text-delta", text: "Cursor SDK" } });
      const customToolResult = options.local?.customTools?.lookup_weather
        ? await options.local.customTools.lookup_weather.execute({ city: "Tokyo" }, { toolCallId: "tool_custom_weather" })
        : undefined;
      const promptText = typeof message === "string" ? message : message.text ?? JSON.stringify(message);
      const runId = `run_${Math.random().toString(16).slice(2, 10)}`;
      const finalResult = customToolResult
        ? `Weather lookup complete for Tokyo: ${JSON.stringify(customToolResult)}`
        : "Cursor SDK streamed an agent response after using the docs tool.";
      return new DemoRun({
        agentId: this.agentId,
        finalResult,
        model: this.model.id,
        runId,
        messages: [
          { type: "system", agent_id: this.agentId, run_id: runId, model: this.model, tools: ["search_docs"] },
          { type: "user", agent_id: this.agentId, run_id: runId, message: { role: "user", content: [{ type: "text", text: promptText }] } },
          { type: "thinking", agent_id: this.agentId, run_id: runId, text: "I should inspect the available Cursor SDK docs." },
          { type: "task", agent_id: this.agentId, run_id: runId, status: "planning", text: "Plan complete." },
          { type: "assistant", agent_id: this.agentId, run_id: runId, message: { role: "assistant", content: [{ type: "tool_use", id: "tool_docs", name: "search_docs", input: { query: "Cursor SDK tracing" } }, { type: "text", text: finalResult }] } },
          { type: "tool_call", agent_id: this.agentId, run_id: runId, call_id: "tool_docs", name: "search_docs", status: "running", args: { query: "Cursor SDK tracing" } },
          { type: "tool_call", agent_id: this.agentId, run_id: runId, call_id: "tool_docs", name: "search_docs", status: "completed", result: { matches: ["Agent.create(options)", "agent.send(message, options)", "run.stream()"] } },
          { type: "status", agent_id: this.agentId, run_id: runId, status: "FINISHED", message: "demo run finished" },
        ],
      });
    }

    close(): void {}
    async reload(): Promise<void> {}
    async [Symbol.asyncDispose](): Promise<void> {}
    async listArtifacts(): Promise<unknown[]> { return []; }
    async downloadArtifact(): Promise<Buffer> { return Buffer.from(""); }
  }

  class Agent {
    static async create(options: AnyRecord = {}): Promise<DemoAgent> { return new DemoAgent(options); }
    static async resume(agentId: string, options: AnyRecord = {}): Promise<DemoAgent> { return new DemoAgent({ ...options, agentId }); }
    static async prompt(message: string | AnyRecord, options: AnyRecord = {}): Promise<AnyRecord> {
      const agent = new DemoAgent(options);
      const run = await agent.send(message, options);
      for await (const _event of run.stream()) {}
      return await run.wait();
    }
    static async getRun(runId: string): Promise<DemoRun> {
      return new DemoRun({ agentId: "agent_restored", finalResult: "Restored run result.", messages: [], model: "cursor-small", runId });
    }
  }

  return { Agent };
}
