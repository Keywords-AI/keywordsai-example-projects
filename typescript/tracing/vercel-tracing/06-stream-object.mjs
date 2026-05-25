import { streamObject } from "ai";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("06_stream_object", async ({ gateway, modelName, runId, telemetry }) => {
  const result = streamObject({
    model: gateway(modelName),
    schema: z.object({
      status: z.string(),
      confidence: z.number(),
      runId: z.string(),
    }),
    prompt: `Run ${runId}: stream JSON with status stable, confidence 0.91, and this run id.`,
    experimental_telemetry: telemetry("stream_object"),
  });

  let latest = {};
  for await (const partial of result.partialObjectStream) {
    latest = partial;
  }

  console.log(JSON.stringify(latest));
});
