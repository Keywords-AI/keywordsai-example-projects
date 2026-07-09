import {
  MODELS,
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
  summarizeChatCompletion,
} from "./_shared.js";

const workflowName = "together-ai-ts-tool-calls";
const respan = createRespan("together-ai-typescript-tools");

const tools = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get a simple weather forecast for a city.",
      parameters: {
        type: "object",
        properties: { city: { type: "string" } },
        required: ["city"],
      },
    },
  },
] as const;

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    return await captureFeature(workflowName, async () => {
      const messages: any[] = [
        { role: "user", content: "Use the get_weather tool for Tokyo, then answer briefly." },
      ];
      const first = await client.chat.completions.create({
        model: MODELS.chat,
        messages,
        tools: tools as any,
        tool_choice: "auto",
        max_tokens: 80,
        temperature: 0,
      });

      const emittedToolCalls = first.choices?.[0]?.message?.tool_calls ?? [];
      const toolCalls = emittedToolCalls.length > 0 ? emittedToolCalls : [
        {
          id: "call_respan_demo_weather",
          type: "function",
          function: { name: "get_weather", arguments: JSON.stringify({ city: "Tokyo" }) },
        },
      ];

      messages.push({
        role: "assistant",
        content: first.choices?.[0]?.message?.content ?? "",
        tool_calls: toolCalls,
      });
      messages.push({
        role: "tool",
        tool_call_id: toolCalls[0].id,
        content: JSON.stringify({ city: "Tokyo", forecast: "clear" }),
      });

      const second = await client.chat.completions.create({
        model: MODELS.chat,
        messages,
        max_tokens: 80,
        temperature: 0,
      });

      return {
        first: summarizeChatCompletion(first),
        second: summarizeChatCompletion(second),
        toolCalls: toolCalls.length,
      };
    });
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
