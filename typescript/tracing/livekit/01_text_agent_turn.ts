import { voice } from "@livekit/agents";
import {
  closeSession,
  createRespan,
  ExampleFakeLLM,
  logExampleResult,
  runWithExampleTrace,
  summarizeRunEvents,
} from "./_shared.js";

const workflowName = "TypeScript LiveKit Text Agent Turn Example";

export async function textAgentTurnExample(): Promise<void> {
  const respan = createRespan("typescript-livekit-text-turn-example");
  await respan.initialize();

  try {
    const events = await runWithExampleTrace(respan, workflowName, async () => {
      const session = new voice.AgentSession({
        llm: new ExampleFakeLLM([
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
        const result = await session
          .run({ userInput: "Give me a short welcome for a travel concierge." })
          .wait();
        return summarizeRunEvents(result);
      } finally {
        await closeSession(session);
      }
    });

    logExampleResult(workflowName, {
      events,
    });
  } finally {
    await respan.shutdown();
  }
}

await textAgentTurnExample();
