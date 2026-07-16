import { Agent } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-basic");

try {
  const agent = new Agent({
    name: "gateway_basic_agent",
    instructions: "Answer in one concise sentence.",
    model: runtime.model,
  });

  const result = await withExampleTrace(
    runtime,
    "openai_agents_gateway_basic.workflow",
    async () =>
      await runtime.runner.run(
        agent,
        `Run ${runtime.runId}: explain what Respan traces capture.`,
        {
          maxTurns: 1,
        },
      ),
  );

  console.log(String(result.finalOutput ?? ""));
} finally {
  await shutdownRuntime(runtime);
}
