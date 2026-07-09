import { logExampleResult, runCohereWorkflow } from "./_shared.js";

const workflowName = "cohere_ts_v2_streaming_chat";

const text = await runCohereWorkflow(workflowName, async ({ clientV2 }) => {
  const stream = await clientV2.chatStream({
    model: "command-a-03-2025",
    messages: [{ role: "user", content: "Stream a short status." }],
  });

  let content = "";
  for await (const event of stream) {
    if (event.type === "content-delta") {
      content += event.delta?.message?.content?.text ?? "";
    }
  }
  return content;
});

logExampleResult(workflowName, { content: text });
