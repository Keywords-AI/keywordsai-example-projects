import { logExampleResult, runCohereWorkflow } from "./_shared.js";

const workflowName = "cohere_ts_legacy_generate";

const result = await runCohereWorkflow(workflowName, async ({ client }) => {
  const generated = await client.generate({
    model: "command",
    prompt: "Write a concise status.",
  });

  const stream = await client.generateStream({
    model: "command",
    prompt: "Write a concise streaming status.",
  });
  let streamed = "";
  for await (const event of stream) {
    if (event.eventType === "text-generation") {
      streamed += event.text;
    }
  }

  return { generated, streamed };
});

logExampleResult(workflowName, {
  generated: result.generated.generations?.[0]?.text,
  streamed: result.streamed,
});
