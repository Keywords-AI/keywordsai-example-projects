import {
  MODELS,
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
} from "./_shared.js";

const workflowName = "together-ai-ts-text-completion-embedding";
const respan = createRespan("together-ai-typescript-text-embedding");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    const completion = await captureFeature("together text completion", async () => {
      const response = await client.completions.create({
        model: MODELS.completion,
        prompt: "Complete this sentence in five words: Respan tracing makes",
        max_tokens: 24,
        temperature: 0,
      });
      return {
        model: response.model,
        text: response.choices?.[0]?.text ?? "",
        usage: response.usage ?? null,
      };
    });

    const embedding = await captureFeature("together embedding", async () => {
      const response = await client.embeddings.create({
        model: MODELS.embedding,
        input: ["Respan traces Together AI TypeScript SDK calls."],
      });
      return {
        model: response.model,
        vectors: response.data.length,
        dimensions: response.data[0]?.embedding?.length ?? 0,
      };
    });

    return { completion, embedding };
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
