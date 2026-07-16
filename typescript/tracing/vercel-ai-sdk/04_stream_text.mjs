import { streamText } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("stream_text", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await streamText({
    model: gateway.chat(modelName),
    prompt: `Run ${runId}: stream one concise sentence about AI SDK telemetry.`,
    telemetry: telemetry("stream_text"),
  });

  let text = "";
  for await (const delta of result.textStream) {
    text += delta;
  }

  console.log(text.slice(0, 240));
});
