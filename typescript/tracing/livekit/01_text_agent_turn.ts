import { voice } from "@livekit/agents";
import {
  closeSession,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
  summarizeRunEvents,
} from "./_shared.js";

const workflowName = "TypeScript LiveKit Text Agent Turn Example";

export async function textAgentTurnExample(): Promise<void> {
  const respan = createRespan("typescript-livekit-text-turn-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const session = new voice.AgentSession({
        llm: new voice.testing.FakeLLM([
          {
            input: "Give me a short welcome for a travel concierge.",
            content: "Welcome. I can help plan a focused city itinerary.",
          },
        ]),
      });

      const agent = new voice.Agent({
        id: "travel_concierge",
        instructions: "Answer in one concise sentence.",
      });

      try {
        await session.start({ agent, record: false });
        return await session
          .run({ userInput: "Give me a short welcome for a travel concierge." })
          .wait();
      } finally {
        await closeSession(session);
      }
    });

    logExampleResult(workflowName, {
      events: summarizeRunEvents(result),
    });
  } finally {
  }
}

await textAgentTurnExample();
