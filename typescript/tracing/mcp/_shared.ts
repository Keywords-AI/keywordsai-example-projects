import dotenv from "dotenv";
import * as MCPClientModule from "@modelcontextprotocol/sdk/client/index.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import * as MCPServerModule from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Respan } from "@respan/respan";
import { MCPInstrumentor } from "@respan/instrumentation-mcp";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as z from "zod/v4";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

export const RUN_ID = process.env.RESPAN_EXAMPLE_RUN_ID || `mcp-ts-${Date.now()}`;

export interface DemoMcpEnvironment {
  client: Client;
  close: () => Promise<void>;
  server: McpServer;
}

export function createRespan(appName: string): Respan {
  if (!process.env.RESPAN_API_KEY) {
    throw new Error("Set RESPAN_API_KEY in the respan-example-projects repo root .env file.");
  }

  return new Respan({
    apiKey: process.env.RESPAN_API_KEY,
    baseURL: process.env.RESPAN_BASE_URL,
    appName,
    instrumentations: [
      new MCPInstrumentor({
        clientModule: MCPClientModule,
        serverModule: MCPServerModule,
      }),
    ],
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
        example: "typescript-mcp",
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

export async function createDemoMcpEnvironment(): Promise<DemoMcpEnvironment> {
  const server = new McpServer({
    name: "respan-demo-mcp-server",
    version: "1.0.0",
  });

  server.registerTool(
    "summarize_city",
    {
      title: "Summarize city",
      description: "Return a concise city summary.",
      inputSchema: {
        city: z.string().describe("City name"),
      },
    },
    async ({ city }) => ({
      content: [
        {
          type: "text",
          text: `${city} is known for culture, food, and resilient urban design.`,
        },
      ],
      structuredContent: {
        city,
        summary: `${city} has a compact, transit-friendly center.`,
      },
    }),
  );

  server.registerTool(
    "compare_cities",
    {
      title: "Compare cities",
      description: "Compare two cities for a short travel brief.",
      inputSchema: {
        firstCity: z.string(),
        secondCity: z.string(),
      },
    },
    async ({ firstCity, secondCity }) => ({
      content: [
        {
          type: "text",
          text: `${firstCity} is better for museums; ${secondCity} is better for cafes.`,
        },
      ],
    }),
  );

  server.registerResource(
    "city_notes_static",
    "demo://city/paris",
    {
      title: "Paris notes",
      description: "Static notes for the Paris demo resource.",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "text/plain",
          text: "Paris: museums, transit, river walks, and dense neighborhoods.",
        },
      ],
    }),
  );

  server.registerResource(
    "city_notes_dynamic",
    new ResourceTemplate("demo://city/{city}", { list: undefined }),
    {
      title: "City notes",
      description: "Dynamic city notes resource.",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "text/plain",
          text: `Notes for ${uri.pathname.replace(/^\//, "") || "unknown city"}.`,
        },
      ],
    }),
  );

  server.registerPrompt(
    "city_brief",
    {
      title: "City brief",
      description: "Build a short city brief prompt.",
      argsSchema: {
        city: z.string(),
      },
    },
    ({ city }) => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Write a concise travel brief for ${city}.`,
          },
        },
      ],
    }),
  );

  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await server.connect(serverTransport);

  const client = new Client({
    name: "respan-mcp-example-client",
    version: "1.0.0",
  });
  await client.connect(clientTransport);

  return {
    client,
    server,
    close: async () => {
      await client.close();
      await server.close();
    },
  };
}
