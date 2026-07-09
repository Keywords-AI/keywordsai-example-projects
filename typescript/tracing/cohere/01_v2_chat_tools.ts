import { logExampleResult, runCohereWorkflow } from "./_shared.js";

const workflowName = "cohere_ts_v2_chat_tools";

const result = await runCohereWorkflow(workflowName, async ({ clientV2 }) => {
  return clientV2.chat({
    model: "command-a-03-2025",
    messages: [{ role: "user", content: "Use a tool to summarize Respan tracing." }],
    tools: [
      {
        type: "function",
        function: {
          name: "lookup_docs",
          description: "Lookup product documentation.",
          parameters: {
            type: "object",
            properties: { topic: { type: "string" } },
            required: ["topic"],
          },
        },
      },
    ],
  });
});

logExampleResult(workflowName, {
  content: result.message?.content,
  toolCalls: result.message?.toolCalls?.length ?? 0,
});
