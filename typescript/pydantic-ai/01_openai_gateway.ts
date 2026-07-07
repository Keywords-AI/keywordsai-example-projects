import { createRuntime, firstText, runPydanticAIChat } from "./_runtime.js";

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-openai",
  model: process.env.RESPAN_OPENAI_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4o-mini",
});

try {
  const messages = [
    { role: "system" as const, content: "You answer in one concise sentence." },
    { role: "user" as const, content: "What does Respan help developers observe?" },
  ];

  const response = await runPydanticAIChat(runtime, {
    spanName: "pydantic_ai.openai_gateway",
    provider: "openai",
    messages,
    fn: async () =>
      await runtime.client.chat.completions.create({
        model: runtime.model,
        messages,
      }),
    outputMessages: (result) => [
      { role: "assistant", content: firstText(result) },
    ],
    usage: (result) => ({
      inputTokens: result.usage?.prompt_tokens,
      outputTokens: result.usage?.completion_tokens,
      totalTokens: result.usage?.total_tokens,
    }),
  });

  console.log(JSON.stringify({
    provider: "openai",
    model: runtime.model,
    text: firstText(response),
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
