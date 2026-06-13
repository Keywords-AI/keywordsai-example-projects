import {
  createAzureClient,
  createRespan,
  installMockAzureOpenAIResponses,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Azure OpenAI Embeddings Example";

export async function embeddingsExample(): Promise<void> {
  const restoreMocks = installMockAzureOpenAIResponses();
  const respan = createRespan("typescript-azure-openai-embeddings-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const client = createAzureClient("text-embedding-3-small");
      return await client.embeddings.create({
        model: "text-embedding-3-small",
        input: [
          "Respan captures Azure OpenAI embedding calls.",
          "Embedding vectors should not be exported as span attributes.",
        ],
        extraAttributes: {
          "respan.metadata.azure_feature": "embeddings",
        },
      } as any);
    });

    logExampleResult(workflowName, {
      embeddingCount: result.data.length,
      vectorDimensions: result.data[0]?.embedding.length,
      model: result.model,
    });
  } finally {
    await respan.shutdown();
    restoreMocks();
  }
}

await embeddingsExample();
