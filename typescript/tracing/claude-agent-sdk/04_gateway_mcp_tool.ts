import { createSdkMcpServer, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod/v4";
import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-mcp-tool");

const describeRunTool = tool(
  "describe_run",
  "Return deterministic trace metadata for a Respan example run.",
  {
    topic: z.string(),
  },
  async ({ topic }) => ({
    content: [
      {
        type: "text",
        text: JSON.stringify({
          topic,
          runId: runtime.runId,
          routedThroughGateway: true,
        }),
      },
    ],
  }),
  {
    alwaysLoad: true,
  },
);

const mcpServer = createSdkMcpServer({
  name: "respan_example",
  version: "0.1.0",
  instructions: "Use describe_run when asked for deterministic trace metadata.",
  tools: [describeRunTool],
  alwaysLoad: true,
});

try {
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_mcp_tool.workflow",
      associationProperties: {
        run_id: runtime.runId,
        example: "claude-agent-sdk",
      },
    },
    async () =>
      await queryForResult(
        runtime,
        `Run ${runtime.runId}: use the describe_run MCP tool with topic "mcp instrumentation", then summarize the tool result.`,
        {
          maxTurns: 2,
          tools: [],
          allowedTools: ["mcp__respan_example__describe_run"],
          strictMcpConfig: true,
          mcpServers: {
            respan_example: mcpServer,
          },
        },
      ),
  );

  console.log(`subtype: ${String(result.subtype ?? "unknown")}`);
} finally {
  await shutdownRuntime(runtime);
}
