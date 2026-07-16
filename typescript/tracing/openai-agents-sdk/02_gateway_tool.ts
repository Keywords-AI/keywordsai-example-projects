import { Agent, tool } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-tool");

const weatherTool = tool({
  name: "lookup_weather",
  description: "Return deterministic weather for a city.",
  parameters: {
    type: "object",
    properties: {
      city: { type: "string" },
    },
    required: ["city"],
    additionalProperties: false,
  },
  strict: true,
  execute: async (input) => {
    const city = typeof input === "object" && input && "city" in input
      ? String((input as { city: unknown }).city)
      : "unknown";
    return { city, condition: "clear", windKph: 8, runId: runtime.runId };
  },
});

try {
  const agent = new Agent({
    name: "gateway_tool_agent",
    instructions: "Use the weather tool when the user asks for weather.",
    model: runtime.model,
    tools: [weatherTool],
  });

  const result = await withExampleTrace(
    runtime,
    "openai_agents_gateway_tool.workflow",
    async () =>
      await runtime.runner.run(
        agent,
        `Run ${runtime.runId}: look up Tokyo weather and summarize it.`,
        {
          maxTurns: 3,
        },
      ),
  );

  console.log(String(result.finalOutput ?? ""));
} finally {
  await shutdownRuntime(runtime);
}
