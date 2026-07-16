import {
  createDemoCursorSDKModule,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Cursor SDK Agent Prompt Example";

export async function agentPromptExample(): Promise<void> {
  const cursorSdk = createDemoCursorSDKModule();
  const respan = createRespan("typescript-cursor-sdk-agent-prompt-example", cursorSdk);
  await respan.initialize();
  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      return await cursorSdk.Agent.prompt("Summarize how Cursor SDK runs are traced.", {
        name: "cursor_prompt_agent",
        model: { id: "cursor-small" },
      });
    });
    logExampleResult(workflowName, { status: result.status, result: result.result, model: result.model });
  } finally {
  }
}

await agentPromptExample();
