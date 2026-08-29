import { MODEL, createRuntime, runCase } from "./_shared.js";

const caseId = "tool";
const { client, respan } = createRuntime();

try {
  const output = await runCase(respan, caseId, async () => {
    const tools = [
      {
        name: "lookup_weather",
        description: "Look up a city's weather.",
        input_schema: {
          type: "object" as const,
          properties: { city: { type: "string" } },
          required: ["city"],
        },
      },
    ];
    const first = await client.messages.create({
      model: MODEL,
      max_tokens: 100,
      tools,
      tool_choice: { type: "tool", name: "lookup_weather" },
      messages: [{ role: "user", content: "What is the weather in Tokyo?" }],
    });
    const toolUse = first.content.find((block) => block.type === "tool_use");
    if (!toolUse || toolUse.type !== "tool_use") {
      throw new Error("Anthropic did not return the forced tool call.");
    }

    const second = await client.messages.create({
      model: MODEL,
      max_tokens: 100,
      tools,
      messages: [
        { role: "user", content: "What is the weather in Tokyo?" },
        { role: "assistant", content: first.content },
        {
          role: "user",
          content: [
            {
              type: "tool_result",
              tool_use_id: toolUse.id,
              content: "sunny, 24 C",
            },
          ],
        },
      ],
    });

    return {
      toolCallId: toolUse.id,
      toolName: toolUse.name,
      output: second.content
        .filter((block) => block.type === "text")
        .map((block) => block.text)
        .join(" "),
    };
  });
  console.log(JSON.stringify({ caseId, output }));
} finally {
  await respan.shutdown();
}
