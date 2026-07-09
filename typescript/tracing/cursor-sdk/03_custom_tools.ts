import {
  createDemoCursorSDKModule,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Cursor SDK Custom Tools Example";

export async function customToolsExample(): Promise<void> {
  const cursorSdk = createDemoCursorSDKModule();
  const respan = createRespan("typescript-cursor-sdk-custom-tools-example", cursorSdk);
  await respan.initialize();
  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const agent = await cursorSdk.Agent.create({ name: "cursor_custom_tools_agent", model: { id: "cursor-small" } });
      const run = await agent.send("Look up Tokyo weather with a local custom tool.", {
        local: {
          customTools: {
            lookup_weather: {
              description: "Return deterministic weather for a city.",
              inputSchema: { type: "object", properties: { city: { type: "string" } }, required: ["city"] },
              execute: async ({ city }: { city: string }) => ({ city, condition: "clear", temperatureC: 21 }),
            },
          },
        },
      });
      const waitResult = await run.wait();
      return { runId: run.id, waitResult };
    });
    logExampleResult(workflowName, { runId: result.runId, status: result.waitResult.status, result: result.waitResult.result });
  } finally {
    await respan.flush();
  }
}

await customToolsExample();
