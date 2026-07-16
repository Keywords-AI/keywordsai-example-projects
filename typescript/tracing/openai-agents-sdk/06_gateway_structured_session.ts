import { Agent, MemorySession } from "@openai/agents";
import { z } from "zod";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-structured-session");

const SessionSummary = z.object({
  runId: z.string(),
  rememberedTopic: z.string(),
  nextAction: z.string(),
});

try {
  const session = new MemorySession({
    sessionId: `session-${runtime.runId}`,
  });
  const agent = new Agent({
    name: "gateway_structured_session_agent",
    instructions:
      "Use the conversation session to remember prior turns. Always return structured data matching the output schema.",
    model: runtime.model,
    outputType: SessionSummary,
  });

  const { first, second } = await withExampleTrace(
    runtime,
    "openai_agents_gateway_structured_session.workflow",
    async () => {
      const firstResult = await runtime.runner.run(
        agent,
        `Run ${runtime.runId}: remember that the target topic is session-aware trace correlation.`,
        {
          maxTurns: 2,
          session,
        },
      );
      const secondResult = await runtime.runner.run(
        agent,
        "Use the prior session context and return the remembered topic.",
        {
          maxTurns: 2,
          session,
        },
      );
      return {
        first: firstResult.finalOutput,
        second: secondResult.finalOutput,
      };
    },
  );

  console.log(JSON.stringify({ first, second }, null, 2));
} finally {
  await shutdownRuntime(runtime);
}
