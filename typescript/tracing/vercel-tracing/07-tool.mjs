import { generateText, tool } from "ai";
import assert from "node:assert/strict";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("07_tool", async ({ gateway, modelName, runId, telemetry }) => {
  const weather = tool({
    description: "Return deterministic weather for the requested city.",
    parameters: z.object({
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
    model: gateway(modelName),
    prompt: `Run ${runId}: call the weather tool for Tokyo, then summarize the result.`,
    tools: { weather },
    maxSteps: 3,
    experimental_prepareStep: ({ stepNumber }) =>
      stepNumber === 0
        ? { toolChoice: { type: "tool", toolName: "weather" } }
        : { toolChoice: "none" },
    experimental_telemetry: telemetry("tool"),
  });

  assert.equal(result.steps.length, 2);
  assert.equal(result.steps[0].toolCalls.length, 1);
  assert.equal(result.steps[0].toolResults.length, 1);
  assert.ok(result.text.includes("Tokyo"), "final answer should include Tokyo");
  assert.ok(result.text.length > 0, "final answer should not be empty");

  console.log(`text chars: ${result.text.length}`);
  console.log(result.text.slice(0, 240));
});
