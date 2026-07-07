import { generateObject } from "ai";
import { z } from "zod";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("generate_object", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await generateObject({
    model: gateway.chat(modelName),
    schemaName: "VercelTelemetrySummary",
    schemaDescription: "Short structured summary of Vercel AI SDK telemetry coverage.",
    schema: z.object({
      runId: z.string(),
      route: z.string(),
      features: z.array(z.string()).min(2).max(4),
    }),
    prompt: `Run ${runId}: return a structured object about gateway-routed AI SDK telemetry.`,
    telemetry: telemetry("generate_object"),
  });

  console.log(JSON.stringify(result.object, null, 2));
});
