import assert from "node:assert/strict";
import { isStepCount, ToolLoopAgent, tool } from "ai";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("tool_loop_agent", async ({ gateway, modelName, runId, telemetry }) => {
  const lookupTrace = tool({
    description: "Return deterministic trace metadata for an example run.",
    inputSchema: z.object({
      topic: z.string(),
    }),
    execute: async ({ topic }) => ({
      topic,
      runId,
      exported: true,
    }),
  });

  const agent = new ToolLoopAgent({
    id: "respan-gateway-tool-loop-agent",
    model: gateway.chat(modelName),
    instructions:
      "Use lookupTrace exactly once when asked for trace metadata, then give a concise final answer.",
    tools: { lookupTrace },
    stopWhen: isStepCount(3),
    prepareStep: ({ stepNumber }) =>
      stepNumber === 0
        ? { toolChoice: { type: "tool", toolName: "lookupTrace" } }
        : { toolChoice: "none" },
    telemetry: telemetry("tool_loop_agent"),
  });

  const result = await agent.generate({
    prompt: `Run ${runId}: look up trace metadata for gateway agent coverage and summarize it.`,
  });

  assert.ok(result.steps.length >= 1);
  assert.equal(result.steps[0].toolCalls.length, 1);
  console.log(result.text.slice(0, 240));
});
