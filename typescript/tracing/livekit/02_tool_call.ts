import { llm, voice } from "@livekit/agents";
import { z } from "zod";
import {
  closeSession,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
  summarizeRunEvents,
} from "./_shared.js";

const workflowName = "TypeScript LiveKit Tool Call Example";

export async function toolCallExample(): Promise<void> {
  const respan = createRespan("typescript-livekit-tool-call-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const session = new voice.AgentSession({
        llm: new voice.testing.FakeLLM([
          {
            input: "What is the weather in Tokyo?",
            toolCalls: [{ name: "get_weather", args: { city: "Tokyo" } }],
          },
          {
            input: "Tokyo forecast: clear skies and light wind.",
            content: "Tokyo forecast: clear skies and light wind.",
          },
        ]),
      });

      const agent = new voice.Agent({
        id: "weather_agent",
        instructions: "Use tools when weather data is requested.",
        tools: {
          get_weather: llm.tool({
            description: "Return a compact weather forecast for a city.",
            parameters: z.object({ city: z.string() }),
            execute: async ({ city }) => city + " forecast: clear skies and light wind.",
          }),
        },
      });

      try {
        await session.start({ agent, record: false });
        return await session.run({ userInput: "What is the weather in Tokyo?" }).wait();
      } finally {
        await closeSession(session);
      }
    });

    logExampleResult(workflowName, {
      events: summarizeRunEvents(result),
    });
  } finally {
    await respan.flush();
  }
}

await toolCallExample();
