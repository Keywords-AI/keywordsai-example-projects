import { Settings, tool } from "llamaindex";
import { TracedMockLLM } from "./_deterministic_llm.js";
import { runNamedWorkflow } from "./_runtime.js";

export const WORKFLOW_NAME = "llama_index_ts_tool_call";

const weatherTool = tool(
  (input: { city: string }) => ({
    city: input.city,
    forecast: "clear skies",
    temperature_c: 22,
  }),
  {
    name: "lookup_city_weather",
    description: "Lookup a compact weather report for a city.",
    parameters: {
      type: "object",
      properties: {
        city: {
          type: "string",
          description: "City name to look up.",
        },
      },
      required: ["city"],
      additionalProperties: false,
    } as any,
  },
);

async function main(): Promise<void> {
  const { result, finalAnswer } = await runNamedWorkflow(WORKFLOW_NAME, async () => {
    const llm = new TracedMockLLM({
      responseMessage: "Calling the requested weather tool.",
      mockToolCallResponse: {
        toolCalls: [{
          id: "call_weather_tokyo",
          name: "lookup_city_weather",
          input: { city: "Tokyo" },
        }],
      },
    });
    Settings.llm = llm;

    const result = await llm.exec({
      messages: [
        {
          role: "user",
          content:
            "Use the lookup_city_weather tool for Tokyo, then return the tool result.",
        },
      ],
      tools: [weatherTool],
    });

    const toolResultMessage = result.newMessages.find(
      (message) =>
        message.options &&
        typeof message.options === "object" &&
        "toolResult" in message.options,
    );
    const toolResultOptions = toolResultMessage?.options as
      | { toolResult?: { result?: unknown } }
      | undefined;
    const toolResult = toolResultOptions?.toolResult?.result;

    const finalLlm = new TracedMockLLM({
      responseMessage: "Tokyo weather: clear skies, 22 C.",
    });
    Settings.llm = finalLlm;

    const finalAnswer = await finalLlm.complete({
      prompt: [
        "Use this weather tool result to answer the user.",
        "Return exactly: Tokyo weather: clear skies, 22 C.",
        `Tool result: ${JSON.stringify(toolResult)}`,
      ].join("\n"),
    });

    return { result, finalAnswer };
  });

  console.log(
    `[${WORKFLOW_NAME}] tool_calls=${result.toolCalls.length} messages=${result.newMessages.length} final=${finalAnswer.text}`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
