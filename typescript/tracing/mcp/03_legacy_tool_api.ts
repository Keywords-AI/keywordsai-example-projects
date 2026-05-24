import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript MCP Legacy Tool API Example";

export async function legacyToolApiExample(): Promise<void> {
  const respan = createRespan("typescript-mcp-legacy-tool-api-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const server = new McpServer({ name: "legacy-tool-api-server", version: "1.0.0" });
      server.tool("legacy_echo", "Echo an input value.", {}, async () => ({
        content: [{ type: "text", text: "legacy echo ok" }],
      }));

      const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
      await server.connect(serverTransport);
      const client = new Client({ name: "legacy-tool-api-client", version: "1.0.0" });
      await client.connect(clientTransport);

      try {
        const tools = await client.listTools();
        const echo = await client.callTool({ name: "legacy_echo", arguments: {} });
        return { tools, echo };
      } finally {
        await client.close();
        await server.close();
      }
    });

    logExampleResult(workflowName, {
      toolNames: result.tools.tools.map((tool) => tool.name),
      content: result.echo.content,
    });
  } finally {
    await respan.flush();
  }
}

await legacyToolApiExample();
