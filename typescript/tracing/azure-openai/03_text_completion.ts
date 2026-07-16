import {
  createAzureClient,
  createRespan,
  installMockAzureOpenAIResponses,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Azure OpenAI Text Completion Example";

export async function textCompletionExample(): Promise<void> {
  const restoreMocks = installMockAzureOpenAIResponses();
  const respan = createRespan("typescript-azure-openai-text-completion-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const client = createAzureClient("gpt-35-turbo-instruct");
      return await client.completions.create({
        model: "gpt-35-turbo-instruct",
        prompt: "Write one sentence about Respan tracing.",
        max_tokens: 32,
        extraAttributes: {
          "respan.metadata.azure_feature": "text_completion",
        },
      } as any);
    });

    logExampleResult(workflowName, {
      text: result.choices[0]?.text,
      model: result.model,
    });
  } finally {
    await respan.shutdown();
    restoreMocks();
  }
}

await textCompletionExample();
