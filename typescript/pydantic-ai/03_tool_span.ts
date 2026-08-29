import {
  createRuntime,
  firstText,
  runPydanticAIChat,
  runPydanticAITool,
  runPydanticAIWorkflow,
} from "./_runtime.js";

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-tools",
  model: process.env.RESPAN_OPENAI_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4o-mini",
});

async function lookupStatus(args: { service: string }): Promise<string> {
  return await runPydanticAITool("lookup_status", args, async () => {
    return `${args.service} tracing pipeline is healthy`;
  });
}

try {
  const { response, toolResult } = await runPydanticAIWorkflow(runtime, {
    workflowName: "pydantic_ai.tool_workflow",
    fn: async () => {
      const toolResult = await lookupStatus({ service: "Respan" });
      const messages = [
        { role: "system" as const, content: "You summarize tool results." },
        { role: "user" as const, content: `Tool result: ${toolResult}` },
      ];
      const toolDefinitions = [
        {
          name: "lookup_status",
          description: "Looks up service status",
          parameters: {
            type: "object",
            properties: {
              service: { type: "string" },
            },
            required: ["service"],
          },
        },
      ];

      const response = await runPydanticAIChat(runtime, {
        spanName: "pydantic_ai.tool_gateway",
        provider: "openai",
        messages,
        toolDefinitions,
        fn: async () =>
          await runtime.client.chat.completions.create({
            model: runtime.model,
            messages,
          }),
        outputMessages: (result) => [
          { role: "assistant", content: firstText(result) },
        ],
        usage: (result) => ({
          inputTokens: result.usage?.prompt_tokens,
          outputTokens: result.usage?.completion_tokens,
          totalTokens: result.usage?.total_tokens,
        }),
      });
      return { response, toolResult };
    },
  });

  console.log(JSON.stringify({
    provider: "openai",
    model: runtime.model,
    toolResult,
    text: firstText(response),
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
