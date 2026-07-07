import { generateText } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("generate_text", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await generateText({
    model: gateway.chat(modelName),
    prompt: `Run ${runId}: reply with one concise sentence about AI SDK 7 telemetry.`,
    telemetry: telemetry("generate_text"),
  });

  console.log(result.text.slice(0, 240));
});
