import {
  createVertexExampleRuntime,
  flushAndShutdown,
  logExampleResult,
  responseFromResult,
  runWithExampleTrace,
  textFromResponse,
  WEATHER_TOOL,
} from "./_shared.js";

const workflowName = "TypeScript VertexAI Generate Content Example";

export async function generateContentExample(): Promise<void> {
  const { mode, model, respan } = await createVertexExampleRuntime(
    "typescript-vertexai-generate-content-example",
    {
      systemInstruction: "Answer in one concise sentence.",
      tools: [WEATHER_TOOL],
      generationConfig: {
        maxOutputTokens: 128,
        temperature: 0.2,
        topP: 0.9,
        topK: 32,
      },
    },
  );

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () =>
      await model.generateContent({
        contents: [
          {
            role: "user",
            parts: [{ text: "Write one sentence about why trace observability matters." }],
          },
        ],
      }),
    );
    const response = await responseFromResult(result);
    logExampleResult(workflowName, {
      mode,
      text: textFromResponse(response),
      usage: response?.usageMetadata,
    });
  } finally {
    await flushAndShutdown(respan);
  }
}

await generateContentExample();
