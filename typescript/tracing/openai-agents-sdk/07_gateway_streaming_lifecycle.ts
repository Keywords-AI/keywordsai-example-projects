import { Agent } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-streaming-lifecycle");
const lifecycleEvents: string[] = [];

runtime.runner.on("agent_start", (_context, agent) => {
  lifecycleEvents.push(`runner:${agent.name}:start`);
});
runtime.runner.on("agent_end", (_context, agent) => {
  lifecycleEvents.push(`runner:${agent.name}:end`);
});

try {
  const agent = new Agent({
    name: "gateway_streaming_lifecycle_agent",
    instructions: "Stream a short answer and keep it under 30 words.",
    model: runtime.model,
  });

  agent.on("agent_start", (_context, startedAgent) => {
    lifecycleEvents.push(`agent:${startedAgent.name}:start`);
  });
  agent.on("agent_end", () => {
    lifecycleEvents.push("agent:end");
  });

  const { finalOutput, eventCount } = await withExampleTrace(
    runtime,
    "openai_agents_gateway_streaming_lifecycle.workflow",
    async () => {
      const streamed = await runtime.runner.run(
        agent,
        `Run ${runtime.runId}: stream why lifecycle hooks matter for traces.`,
        {
          maxTurns: 1,
          stream: true,
        },
      );
      let eventCount = 0;
      for await (const event of streamed) {
        eventCount += 1;
        if (event.type === "agent_updated_stream_event") {
          lifecycleEvents.push(`stream:${event.agent.name}`);
        }
      }
      await streamed.completed;
      return {
        finalOutput: streamed.finalOutput,
        eventCount,
      };
    },
  );

  console.log(JSON.stringify({ finalOutput, eventCount, lifecycleEvents }, null, 2));
} finally {
  await shutdownRuntime(runtime);
}
