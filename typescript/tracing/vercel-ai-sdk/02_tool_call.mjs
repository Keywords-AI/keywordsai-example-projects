import assert from "node:assert/strict";
import { generateText, stepCountIs, tool } from "ai";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("tool_call", async ({ gateway, modelName, runId, telemetry }) => {
  const weather = tool({
    description: "Return deterministic weather for the requested city.",
    inputSchema: z.object({
      city: z.string(),
    }),
    execute: async ({ city }) => ({
      city,
      condition: "clear",
      windKph: 8,
      runId,
    }),
  });

  const result = await generateText({
    model: gateway.chat(modelName),
    prompt: `Run ${runId}: call the weather tool for Tokyo, then summarize the result.`,
    tools: { weather },
    stopWhen: stepCountIs(3),
    prepareStep: ({ stepNumber }) =>
      stepNumber === 0
        ? { toolChoice: { type: "tool", toolName: "weather" } }
        : { toolChoice: "none" },
    telemetry: telemetry("tool_call"),
  });

  assert.ok(result.steps.length >= 1);
  assert.equal(result.steps[0].toolCalls.length, 1);
  assert.equal(result.steps[0].toolResults.length, 1);
  console.log(result.text.slice(0, 240));
});
