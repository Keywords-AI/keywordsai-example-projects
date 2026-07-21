import { defineAgent } from "eve";
import { mockModel } from "eve/evals";

export default defineAgent({
  modelContextWindowTokens: 1_000_000,
  model: mockModel({
    provider: "respan-example",
    modelId: "eve-deterministic-root",
    respond({ lastUserMessage, toolResults }) {
      if (toolResults.length > 0) {
        const result = toolResults.at(-1);
        if (result?.name === "get_weather") {
          return {
            text: "Weather result: " + JSON.stringify(result.output),
            usage: { inputTokens: 31, outputTokens: 11 },
          };
        }
        if (result?.name === "researcher") {
          return {
            text: "Delegated result: " + JSON.stringify(result.output),
            usage: { inputTokens: 37, outputTokens: 13 },
          };
        }
      }

      if (lastUserMessage?.includes("RESPAN_EVE_TOOL")) {
        return {
          toolCalls: [
            {
              id: "weather-call-1",
              name: "get_weather",
              input: { city: "Paris" },
            },
          ],
          usage: { inputTokens: 23, outputTokens: 7 },
        };
      }

      if (lastUserMessage?.includes("RESPAN_EVE_SUBAGENT")) {
        return {
          toolCalls: [
            {
              id: "research-call-1",
              name: "researcher",
              input: {
                message: "Return the deterministic instrumentation marker.",
              },
            },
          ],
          usage: { inputTokens: 29, outputTokens: 8 },
        };
      }

      return {
        text: "Eve basic instrumentation example completed.",
        usage: { inputTokens: 17, outputTokens: 9 },
      };
    },
  }),
});
