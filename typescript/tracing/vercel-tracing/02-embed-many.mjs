import { embedMany } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("02_embed_many", async ({ gateway, embeddingModelName, runId, telemetry }) => {
  const result = await embedMany({
    model: gateway.embedding(embeddingModelName),
    values: [
      `Run ${runId}: checkout latency`,
      `Run ${runId}: rollback mitigation`,
      `Run ${runId}: streaming telemetry`,
    ],
    experimental_telemetry: telemetry("embed_many"),
  });

  console.log(`embedding count: ${result.embeddings.length}`);
});
