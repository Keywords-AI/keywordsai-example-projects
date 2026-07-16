import {
  Agent,
  Graph,
  McpClient,
  Model,
  Swarm,
  tool,
  type AgentResult,
  type BaseModelConfig,
  type ContentBlock,
  type ContentBlockData,
  type Message,
  type ModelStreamEvent,
  type StreamOptions,
  type Usage,
} from "@strands-agents/sdk";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StrandsAgentsInstrumentor } from "@respan/instrumentation-strands-agents";
import { Respan } from "@respan/respan";
import dotenv from "dotenv";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";

const DEFAULT_BASE_URL = "https://api.respan.ai/api";
const STRUCTURED_OUTPUT_TOOL_NAME = "strands_structured_output";

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? `strands-agents-ts-${Date.now()}`;

let rootEnvLoaded = false;
let respanLogsSuppressed = false;
const originalConsoleDebug = console.debug.bind(console);
const originalConsoleInfo = console.info.bind(console);
const originalConsoleLog = console.log.bind(console);

export type DemoMode =
  | "basic"
  | "tool"
  | "streaming"
  | "structured"
  | "graph-researcher"
  | "graph-writer"
  | "swarm-researcher"
  | "swarm-writer"
  | "mcp";

export interface DemoMcpEnvironment {
  client: McpClient;
  close: () => Promise<void>;
  server: McpServer;
}

export const cityBriefSchema = z.object({
  city: z.string(),
  score: z.number(),
  rationale: z.string(),
});

function suppressExampleRespanLogs(): void {
  if (respanLogsSuppressed || process.env.RESPAN_EXAMPLE_DEBUG === "true") {
    return;
  }

  console.debug = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]") || firstArg.startsWith("[Respan Debug]")) {
      return;
    }
    originalConsoleDebug(...args);
  };

  console.info = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]")) {
      return;
    }
    originalConsoleInfo(...args);
  };

  console.log = (...args: unknown[]) => {
    const firstArg = typeof args[0] === "string" ? args[0] : "";
    if (firstArg.startsWith("[Respan]") || firstArg.startsWith("Respan tracing")) {
      return;
    }
    originalConsoleLog(...args);
  };

  respanLogsSuppressed = true;
}

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

export function createRespan(appName: string): Respan {
  loadRootEnv();
  suppressExampleRespanLogs();

  return new Respan({
    apiKey: requireEnv("RESPAN_API_KEY"),
    baseURL: process.env.RESPAN_BASE_URL ?? DEFAULT_BASE_URL,
    appName,
    instrumentations: [new StrandsAgentsInstrumentor()],
    silenceInitializationMessage: true,
  });
}

export async function runStrandsExample<T>(params: {
  appName: string;
  workflowName: string;
  fn: () => Promise<T>;
}): Promise<T> {
  const respan = createRespan(params.appName);
  await respan.initialize();

  try {
    return await respan.propagateAttributes(
      {
        custom_identifier: EXAMPLE_RUN_ID,
        thread_identifier: `strands-agents-ts-thread-${EXAMPLE_RUN_ID}`,
        trace_group_identifier: params.workflowName,
        metadata: {
          example: "strands-agents-typescript",
          run_id: EXAMPLE_RUN_ID,
          workflow_name: params.workflowName,
        },
      },
      async () => await respan.withWorkflow({ name: params.workflowName }, params.fn),
    );
  } finally {
  }
}

export class DeterministicStrandsModel extends Model<BaseModelConfig> {
  private readonly _config: BaseModelConfig;
  private _callCount = 0;

  constructor(private readonly _mode: DemoMode, config: BaseModelConfig = {}) {
    super();
    this._config = {
      modelId: `respan-demo-strands-${_mode}`,
      ...config,
    };
  }

  get callCount(): number {
    return this._callCount;
  }

  updateConfig(modelConfig: BaseModelConfig): void {
    Object.assign(this._config, modelConfig);
  }

  getConfig(): BaseModelConfig {
    return { ...this._config };
  }

  async *stream(messages: Message[], options?: StreamOptions): AsyncIterable<ModelStreamEvent> {
    this._callCount += 1;
    const toolSpecs = options?.toolSpecs ?? [];
    const hasToolResult = messages.some((message) =>
      message.content.some((block) => "toolResult" in block.toJSON()),
    );

    if (toolSpecs.some((spec) => spec.name === STRUCTURED_OUTPUT_TOOL_NAME)) {
      yield* streamToolUse(
        STRUCTURED_OUTPUT_TOOL_NAME,
        `structured-${this._callCount}`,
        this.structuredOutputPayload(),
        usage(20, 8),
      );
      return;
    }

    if (this._mode === "tool" && !hasToolResult) {
      yield* streamToolUse("get_weather", "weather-call-1", { city: "Tokyo" }, usage(18, 4));
      return;
    }

    if (this._mode === "mcp" && !hasToolResult) {
      yield* streamToolUse(
        "summarize_city",
        "mcp-call-1",
        { city: "Lisbon" },
        usage(18, 4),
      );
      return;
    }

    yield* streamText(this.textResponse(messages), {
      usage: usage(this._mode === "streaming" ? 16 : 24, this._mode === "streaming" ? 12 : 10),
      chunkSize: this._mode === "streaming" ? 14 : undefined,
    });
  }

  private structuredOutputPayload(): Record<string, unknown> {
    switch (this._mode) {
      case "structured":
        return {
          city: "Tokyo",
          score: 92,
          rationale: "Reliable transit, compact neighborhoods, and strong food options.",
        };
      case "swarm-researcher":
        return {
          agentId: "swarm-writer",
          message: "Use these Lisbon notes to draft a compact city brief.",
          context: { city: "Lisbon", highlights: ["trams", "riverfront", "tilework"] },
        };
      case "swarm-writer":
        return {
          message: "Lisbon brief: trams, riverfront walks, tilework, and hillside viewpoints.",
        };
      default:
        return { message: this.textResponse([]) };
    }
  }

  private textResponse(messages: Message[]): string {
    if (this._mode === "tool") {
      const forecast = findToolResultText(messages) ?? "sunny with light wind";
      return `The Tokyo forecast is ${forecast}.`;
    }
    if (this._mode === "mcp") {
      const summary = findToolResultText(messages) ?? "Lisbon has river views and compact neighborhoods.";
      return `MCP summary received: ${summary}`;
    }
    if (this._mode === "streaming") {
      return "Streaming Strands agent telemetry through Respan with chunked model output.";
    }
    if (this._mode === "graph-researcher") {
      return "Research notes: Kyoto has temples, rail access, gardens, and compact food districts.";
    }
    if (this._mode === "graph-writer") {
      return "Kyoto brief: temples, reliable rail, gardens, and focused food neighborhoods.";
    }
    return "Hello from Strands Agents TypeScript instrumentation.";
  }
}

export function createAgent(mode: DemoMode, options: Partial<ConstructorParameters<typeof Agent>[0]> = {}): Agent {
  return new Agent({
    id: options.id ?? mode,
    name: options.name ?? readableAgentName(mode),
    description: options.description ?? `Deterministic ${mode} Strands demo agent`,
    model: options.model ?? new DeterministicStrandsModel(mode),
    systemPrompt: options.systemPrompt ?? "Return concise demo responses for Respan tracing examples.",
    printer: false,
    tools: options.tools ?? (mode === "tool" ? [getWeatherTool] : []),
    structuredOutputSchema: options.structuredOutputSchema,
    traceAttributes: options.traceAttributes,
  });
}

export function createGraph(): Graph {
  const researcher = createAgent("graph-researcher", {
    id: "graph-researcher",
    name: "Graph Researcher",
  });
  const writer = createAgent("graph-writer", {
    id: "graph-writer",
    name: "Graph Writer",
  });

  return new Graph({
    id: "strands-demo-graph",
    nodes: [researcher, writer],
    edges: [["graph-researcher", "graph-writer"]],
    maxSteps: 4,
  });
}

export function createSwarm(): Swarm {
  const researcher = createAgent("swarm-researcher", {
    id: "swarm-researcher",
    name: "Swarm Researcher",
    description: "Collects city notes and hands off to the writer.",
  });
  const writer = createAgent("swarm-writer", {
    id: "swarm-writer",
    name: "Swarm Writer",
    description: "Writes the final city brief.",
  });

  return new Swarm({
    id: "strands-demo-swarm",
    nodes: [researcher, writer],
    start: "swarm-researcher",
    maxSteps: 3,
  });
}

export async function createDemoMcpEnvironment(): Promise<DemoMcpEnvironment> {
  const server = new McpServer({
    name: "respan-strands-demo-mcp-server",
    version: "1.0.0",
  });

  server.registerTool(
    "summarize_city",
    {
      title: "Summarize city",
      description: "Return a concise city summary for Strands MCP examples.",
      inputSchema: {
        city: z.string().describe("City name"),
      },
    },
    async ({ city }) => ({
      content: [
        {
          type: "text",
          text: `${city} has river walks, compact neighborhoods, and strong public spaces.`,
        },
      ],
      structuredContent: {
        city,
        summary: `${city} has river walks and compact neighborhoods.`,
      },
    }),
  );

  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await server.connect(serverTransport);

  const client = new McpClient({
    transport: clientTransport,
    applicationName: "respan-strands-mcp-client",
    applicationVersion: "1.0.0",
  });
  await client.connect();

  return {
    client,
    server,
    close: async () => {
      await client.disconnect();
      await server.close();
    },
  };
}

export function resultText(result: AgentResult): string {
  return result.toString();
}

export function multiAgentText(result: { content: readonly ContentBlock[] }): string {
  return result.content.map(contentBlockText).filter(Boolean).join(" ");
}

export function logExampleResult(
  workflowName: string,
  details: Record<string, unknown>,
): void {
  console.log(JSON.stringify({ workflowName, runId: EXAMPLE_RUN_ID, ...details }, null, 2));
}

const getWeatherTool = tool({
  name: "get_weather",
  description: "Return a deterministic weather forecast.",
  inputSchema: z.object({
    city: z.string().describe("City name"),
  }),
  callback: ({ city }) => ({
    city,
    forecast: city === "Tokyo" ? "sunny with light wind" : "clear",
  }),
});

function readableAgentName(mode: DemoMode): string {
  return mode
    .split("-")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

async function* streamText(
  text: string,
  options: { usage: Usage; chunkSize?: number },
): AsyncIterable<ModelStreamEvent> {
  yield { type: "modelMessageStartEvent", role: "assistant" };
  yield { type: "modelContentBlockStartEvent" };
  for (const chunk of chunkText(text, options.chunkSize ?? text.length)) {
    yield {
      type: "modelContentBlockDeltaEvent",
      delta: { type: "textDelta", text: chunk },
    };
  }
  yield { type: "modelContentBlockStopEvent" };
  yield { type: "modelMessageStopEvent", stopReason: "endTurn" };
  yield { type: "modelMetadataEvent", usage: options.usage };
}

async function* streamToolUse(
  name: string,
  toolUseId: string,
  input: Record<string, unknown>,
  tokenUsage: Usage,
): AsyncIterable<ModelStreamEvent> {
  yield { type: "modelMessageStartEvent", role: "assistant" };
  yield {
    type: "modelContentBlockStartEvent",
    start: { type: "toolUseStart", name, toolUseId },
  };
  yield {
    type: "modelContentBlockDeltaEvent",
    delta: { type: "toolUseInputDelta", input: JSON.stringify(input) },
  };
  yield { type: "modelContentBlockStopEvent" };
  yield { type: "modelMessageStopEvent", stopReason: "toolUse" };
  yield { type: "modelMetadataEvent", usage: tokenUsage };
}

function chunkText(text: string, size: number): string[] {
  const chunks: string[] = [];
  for (let index = 0; index < text.length; index += size) {
    chunks.push(text.slice(index, index + size));
  }
  return chunks;
}

function usage(inputTokens: number, outputTokens: number): Usage {
  return {
    inputTokens,
    outputTokens,
    totalTokens: inputTokens + outputTokens,
  };
}

function findToolResultText(messages: Message[]): string | undefined {
  for (const message of messages) {
    for (const block of message.content) {
      const data = block.toJSON() as ContentBlockData;
      if ("toolResult" in data) {
        const content = data.toolResult.content;
        const text = content.map((item) => {
          if (typeof item === "string") {
            return item;
          }
          if (typeof item === "object" && item !== null && "text" in item) {
            return String(item.text);
          }
          if (typeof item === "object" && item !== null && "json" in item) {
            return JSON.stringify(item.json);
          }
          return "";
        }).filter(Boolean).join(" ");
        if (text) {
          return text;
        }
      }
    }
  }
  return undefined;
}

function contentBlockText(block: ContentBlock): string {
  const data = block.toJSON() as ContentBlockData;
  if ("text" in data) {
    return data.text;
  }
  if ("toolResult" in data) {
    return data.toolResult.content.map((item) => JSON.stringify(item)).join(" ");
  }
  if ("toolUse" in data) {
    return `${data.toolUse.name}(${JSON.stringify(data.toolUse.input)})`;
  }
  return "";
}
