import { generateObject } from "ai";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("05_generate_object", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await generateObject({
    model: gateway(modelName),
    schema: z.object({
      status: z.enum(["ok", "warn"]),
      region: z.string(),
      runId: z.string(),
    }),
    prompt: `Run ${runId}: return status ok, region iad1, and this run id as JSON.`,
    experimental_telemetry: telemetry("generate_object"),
  });

  console.log(JSON.stringify(result.object));
});
