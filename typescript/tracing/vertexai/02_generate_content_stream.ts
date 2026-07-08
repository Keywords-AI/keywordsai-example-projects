import {
  createVertexExampleRuntime,
  flushAndShutdown,
  logExampleResult,
  responseFromResult,
  runWithExampleTrace,
  textFromResponse,
} from "./_shared.js";

const workflowName = "TypeScript VertexAI Stream Generate Content Example";

export async function generateContentStreamExample(): Promise<void> {
  const { mode, model, respan } = await createVertexExampleRuntime(
    "typescript-vertexai-generate-content-stream-example",
    {
      systemInstruction: "Keep streamed responses compact.",
      generationConfig: {
        maxOutputTokens: 128,
        temperature: 0.1,
      },
    },
  );

  try {
    const streamResult = await runWithExampleTrace(respan, workflowName, async () =>
      await model.generateContentStream({
        contents: [
          {
            role: "user",
            parts: [{ text: "Stream a short explanation of Vertex AI tracing." }],
          },
        ],
      }),
    );

    const chunks: string[] = [];
    if (streamResult?.stream) {
      for await (const chunk of streamResult.stream) {
        chunks.push(textFromResponse(chunk));
      }
    }
    const response = await responseFromResult(streamResult);

    logExampleResult(workflowName, {
      mode,
      chunks,
      finalText: textFromResponse(response),
      usage: response?.usageMetadata,
    });
  } finally {
    await flushAndShutdown(respan);
  }
}

await generateContentStreamExample();
