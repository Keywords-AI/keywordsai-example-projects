import {
  createAzureClient,
  createRespan,
  installMockAzureOpenAIResponses,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Azure OpenAI Chat Example";

export async function chatCompletionExample(): Promise<void> {
  const restoreMocks = installMockAzureOpenAIResponses();
  const respan = createRespan("typescript-azure-openai-chat-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const client = createAzureClient("gpt-4o-mini");
      return await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are concise." },
          { role: "user", content: "Confirm Azure OpenAI tracing is active." },
        ],
        extraAttributes: {
          "respan.metadata.azure_feature": "chat",
        },
      } as any);
    });

    logExampleResult(workflowName, {
      content: result.choices[0]?.message?.content,
      model: result.model,
    });
  } finally {
    await respan.shutdown();
    restoreMocks();
  }
}

await chatCompletionExample();
