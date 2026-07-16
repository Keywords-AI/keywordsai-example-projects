import { createRuntime, firstText, runPydanticAIChat } from "./_runtime.js";

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-anthropic",
  model:
    process.env.RESPAN_ANTHROPIC_MODEL ??
    process.env.RESPAN_MODEL ??
    "claude-sonnet-4-5",
});

try {
  const messages = [
    { role: "system" as const, content: "You answer in one concise sentence." },
    { role: "user" as const, content: "Name one benefit of gateway-routed LLM calls." },
  ];

  const response = await runPydanticAIChat(runtime, {
    spanName: "pydantic_ai.anthropic_gateway",
    provider: "anthropic",
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
    provider: "anthropic",
    model: runtime.model,
    text: firstText(response),
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
