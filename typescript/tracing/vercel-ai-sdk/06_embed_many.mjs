import assert from "node:assert/strict";
import { embedMany } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("embed_many", async ({ gateway, embeddingModelName, runId, telemetry }) => {
  const result = await embedMany({
    model: gateway.embedding(embeddingModelName),
    values: [
      `Run ${runId}: first embedding input for AI SDK telemetry.`,
      `Run ${runId}: second embedding input for batch embedding telemetry.`,
    ],
    telemetry: telemetry("embed_many"),
  });

  assert.equal(result.embeddings.length, 2);
  console.log(`embedding count: ${result.embeddings.length}`);
});
