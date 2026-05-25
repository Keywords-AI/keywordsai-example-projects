import { embed } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("01_embed", async ({ gateway, embeddingModelName, runId, telemetry }) => {
  const result = await embed({
    model: gateway.embedding(embeddingModelName),
    value: `Run ${runId}: single embedding unit case for Vercel telemetry.`,
    experimental_telemetry: telemetry("embed"),
  });

  console.log(`embedding length: ${result.embedding.length}`);
});
