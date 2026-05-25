import { generateText } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("03_generate_text", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await generateText({
    model: gateway(modelName),
    prompt: `Run ${runId}: reply with one concise sentence about Vercel AI SDK tracing.`,
    experimental_telemetry: telemetry("generate_text"),
  });

  console.log(`text chars: ${result.text.length}`);
  console.log(result.text.slice(0, 240));
});
