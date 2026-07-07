import { EXAMPLE_RUN_ID, createRuntime, firstText, runPydanticAIChat } from "./_runtime.js";

interface Observation {
  runId: string;
  category: string;
  signals: string[];
  confidence: number;
}

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-structured-output",
  model: process.env.RESPAN_OPENAI_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4o-mini",
});

function parseObservation(text: string): Observation {
  const value = JSON.parse(text) as Partial<Observation>;
  if (
    typeof value.runId !== "string" ||
    typeof value.category !== "string" ||
    !Array.isArray(value.signals) ||
    !value.signals.every((signal) => typeof signal === "string") ||
    typeof value.confidence !== "number"
  ) {
    throw new Error(`Invalid structured observation: ${text}`);
  }
  return value as Observation;
}

try {
  const messages = [
    {
      role: "system" as const,
      content:
        "Return only JSON that matches the supplied schema. Do not include markdown fences.",
    },
    {
      role: "user" as const,
      content: `Run ${EXAMPLE_RUN_ID}: classify why typed output validation matters for AI tracing.`,
    },
  ];

  const response = await runPydanticAIChat(runtime, {
    spanName: "pydantic_ai.structured_output_gateway",
    provider: "openai",
    messages,
    attributes: {
      "gen_ai.output.type": "json_schema",
      "gen_ai.output.schema.name": "Observation",
    },
    fn: async () =>
      await runtime.client.chat.completions.create({
        model: runtime.model,
        messages,
        response_format: {
          type: "json_schema",
          json_schema: {
            name: "Observation",
            strict: true,
            schema: {
              type: "object",
              additionalProperties: false,
              properties: {
                runId: { type: "string" },
                category: { type: "string" },
                signals: {
                  type: "array",
                  items: { type: "string" },
                },
                confidence: { type: "number" },
              },
              required: ["runId", "category", "signals", "confidence"],
            },
          },
        },
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

  const observation = parseObservation(firstText(response));
  console.log(JSON.stringify({
    provider: "openai",
    model: runtime.model,
    observation,
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
