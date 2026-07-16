import { embed } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("embed", async ({ gateway, embeddingModelName, runId, telemetry }) => {
  const result = await embed({
    model: gateway.embedding(embeddingModelName),
    value: `Run ${runId}: embedding example for AI SDK 7 telemetry.`,
    telemetry: telemetry("embed"),
  });

  console.log(`embedding length: ${result.embedding.length}`);
});
