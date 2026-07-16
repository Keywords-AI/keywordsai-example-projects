import {
  createDemoMcpEnvironment,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript MCP Client Tool Example";

export async function clientToolCallExample(): Promise<void> {
  const respan = createRespan("typescript-mcp-client-tool-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const env = await createDemoMcpEnvironment();
      try {
        const tools = await env.client.listTools();
        const summary = await env.client.callTool({
          name: "summarize_city",
          arguments: { city: "Paris" },
        });
        return { tools, summary };
      } finally {
        await env.close();
      }
    });

    logExampleResult(workflowName, {
      toolNames: result.tools.tools.map((tool) => tool.name),
      content: result.summary.content,
    });
  } finally {
  }
}

await clientToolCallExample();
