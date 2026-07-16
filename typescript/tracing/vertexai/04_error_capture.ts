import {
  createVertexExampleRuntime,
  flushAndShutdown,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript VertexAI Error Capture Example";

export async function errorCaptureExample(): Promise<void> {
  const { mode, model, respan } = await createVertexExampleRuntime(
    "typescript-vertexai-error-capture-example",
    {
      model: "respan-intentional-error-model",
      systemInstruction: "This example intentionally captures a failed call.",
    },
  );

  try {
    let errorMessage = "";
    await runWithExampleTrace(respan, workflowName, async () => {
      try {
        await model.generateContent("Force an expected Vertex AI error.");
      } catch (error) {
        errorMessage = error instanceof Error ? error.message : String(error);
      }
    });

    logExampleResult(workflowName, {
      mode,
      expectedError: true,
      errorMessage,
    });
  } finally {
    await flushAndShutdown(respan);
  }
}

await errorCaptureExample();
