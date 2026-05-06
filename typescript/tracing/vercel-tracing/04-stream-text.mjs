import { streamText } from "ai";
import { runVercelCase } from "./vercel-common.mjs";

await runVercelCase("04_stream_text", async ({ gateway, modelName, runId, telemetry }) => {
  const result = await streamText({
    model: gateway(modelName),
    prompt: `Run ${runId}: stream two short bullets about telemetry health.`,
    experimental_telemetry: telemetry("stream_text"),
  });

  let streamed = "";
  for await (const chunk of result.textStream) {
    streamed += chunk;
  }

  console.log(`stream chars: ${streamed.length}`);
  console.log(streamed.slice(0, 240));
});
