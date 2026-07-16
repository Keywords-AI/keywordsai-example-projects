import {
  createRuntime,
  firstText,
  runPydanticAIOpenInference,
} from "./_runtime.js";

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-openinference",
  model: process.env.RESPAN_OPENAI_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4o-mini",
});

try {
  const input =
    "Explain in one concise sentence what OpenInference-compatible Pydantic AI spans capture.";

  const response = await runPydanticAIOpenInference(runtime, {
    spanName: "pydantic_ai.openinference_gateway",
    provider: "OpenAI",
    input,
    fn: async () =>
      await runtime.client.chat.completions.create({
        model: runtime.model,
        messages: [
          { role: "system", content: "Answer in one concise sentence." },
          { role: "user", content: input },
        ],
      }),
    output: (result) => firstText(result),
    usage: (result) => ({
      inputTokens: result.usage?.prompt_tokens,
      outputTokens: result.usage?.completion_tokens,
      totalTokens: result.usage?.total_tokens,
    }),
  });

  console.log(JSON.stringify({
    provider: "openinference",
    model: runtime.model,
    text: firstText(response),
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
