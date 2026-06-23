import {
  createDemoCursorSDKModule,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Cursor SDK Agent Stream Example";

export async function agentStreamExample(): Promise<void> {
  const cursorSdk = createDemoCursorSDKModule();
  const respan = createRespan("typescript-cursor-sdk-agent-stream-example", cursorSdk);
  await respan.initialize();
  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const agent = await cursorSdk.Agent.create({ name: "cursor_stream_agent", model: { id: "cursor-small" } });
      const run = await agent.send("Use the docs MCP server and explain Cursor SDK streaming.", {
        mcpServers: { docs: { type: "stdio", command: "node", args: ["docs-server.js"] } },
        onStep: async () => undefined,
        onDelta: async () => undefined,
      });
      const eventTypes: string[] = [];
      for await (const event of run.stream()) eventTypes.push(event.type);
      return { eventTypes, waitResult: await run.wait() };
    });
    logExampleResult(workflowName, { eventTypes: result.eventTypes, status: result.waitResult.status, result: result.waitResult.result });
  } finally {
    await respan.flush();
  }
}

await agentStreamExample();
