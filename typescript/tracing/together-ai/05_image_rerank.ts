import {
  MODELS,
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
} from "./_shared.js";

const workflowName = "together-ai-ts-image-rerank";
const respan = createRespan("together-ai-typescript-image-rerank");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    const image = await captureFeature("together image generation", async () => {
      const response = await client.images.generate({
        model: MODELS.image,
        prompt: "A small clean diagram of connected observability spans",
        n: 1,
        width: 512,
        height: 512,
        response_format: "url",
      });
      return {
        model: response.model,
        images: response.data.length,
        firstType: response.data[0]?.type ?? null,
      };
    });

    const rerank = await captureFeature("together rerank", async () => {
      const response = await client.rerank.create({
        model: MODELS.rerank,
        query: "Which document mentions tracing?",
        documents: [
          "Respan captures traces and spans for model calls.",
          "This document is about invoice processing.",
          "A recipe for tomato soup.",
        ],
        top_n: 2,
        return_documents: true,
      });
      return {
        model: response.model,
        results: response.results.length,
        topIndex: response.results[0]?.index ?? null,
        usage: response.usage ?? null,
      };
    });

    return { image, rerank };
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
