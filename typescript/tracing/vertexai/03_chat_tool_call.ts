import {
  createVertexExampleRuntime,
  flushAndShutdown,
  functionCallsFromResponse,
  logExampleResult,
  responseFromResult,
  runWithExampleTrace,
  textFromResponse,
  WEATHER_TOOL,
} from "./_shared.js";

const workflowName = "TypeScript VertexAI Chat Tool Example";

export async function chatToolCallExample(): Promise<void> {
  const { mode, model, respan } = await createVertexExampleRuntime(
    "typescript-vertexai-chat-tool-example",
    {
      systemInstruction: "Use the weather lookup function when weather is requested.",
      tools: [WEATHER_TOOL],
      generationConfig: {
        maxOutputTokens: 128,
        temperature: 0,
      },
    },
  );

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const chat = model.startChat();
      const toolResult = await chat.sendMessage("Use a function to check the weather in Tokyo.");
      const streamResult = await chat.sendMessageStream("Then stream one sentence about the result.");
      if (streamResult?.stream) {
        for await (const _chunk of streamResult.stream) {
          // Consume the stream so the SDK resolves the final response.
        }
      }
      return {
        toolResponse: await responseFromResult(toolResult),
        streamResponse: await responseFromResult(streamResult),
      };
    });

    logExampleResult(workflowName, {
      mode,
      toolCalls: functionCallsFromResponse(result.toolResponse),
      streamedText: textFromResponse(result.streamResponse),
      usage: result.streamResponse?.usageMetadata,
    });
  } finally {
    await flushAndShutdown(respan);
  }
}

await chatToolCallExample();
