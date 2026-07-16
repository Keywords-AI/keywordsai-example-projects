import {
  EXAMPLE_RUN_ID,
  createRuntime,
  firstText,
  runPydanticAIAgent,
  runPydanticAIChat,
  runPydanticAIRunningTools,
  runPydanticAITool,
} from "./_runtime.js";

const runtime = await createRuntime({
  appName: "pydantic-ai-typescript-agent-workflow",
  model: process.env.RESPAN_OPENAI_MODEL ?? process.env.RESPAN_MODEL ?? "gpt-4o-mini",
});

const toolDefinitions = [
  {
    name: "lookup_trace_plan",
    description: "Returns a deterministic trace plan for a run.",
    parameters: {
      type: "object",
      properties: {
        runId: { type: "string" },
      },
      required: ["runId"],
    },
  },
];

try {
  const messages = [
    {
      role: "system" as const,
      content: "You are a compact tracing agent that summarizes tool results.",
    },
    {
      role: "user" as const,
      content: `Run ${EXAMPLE_RUN_ID}: create a trace plan summary.`,
    },
  ];

  const response = await runPydanticAIAgent(runtime, {
    agentName: "pydantic_ai.trace_planner_agent",
    messages,
    toolDefinitions,
    fn: async () => {
      const toolResult = await runPydanticAIRunningTools(
        ["lookup_trace_plan"],
        async () =>
          await runPydanticAITool(
            "lookup_trace_plan",
            { runId: EXAMPLE_RUN_ID },
            async () => ({
              runId: EXAMPLE_RUN_ID,
              steps: ["collect spans", "validate logs", "check parent-child traces"],
            }),
          ),
      );
      return await runPydanticAIChat(runtime, {
        spanName: "pydantic_ai.agent_gateway_chat",
        provider: "openai",
        messages: [
          ...messages,
          {
            role: "user" as const,
            content: `Tool result: ${JSON.stringify(toolResult)}`,
          },
        ],
        toolDefinitions,
        fn: async () =>
          await runtime.client.chat.completions.create({
            model: runtime.model,
            messages: [
              ...messages,
              {
                role: "user",
                content: `Tool result: ${JSON.stringify(toolResult)}`,
              },
            ],
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
    },
    finalResult: (result) => ({
      model: runtime.model,
      text: firstText(result),
    }),
  });

  console.log(JSON.stringify({
    provider: "openai",
    model: runtime.model,
    text: firstText(response),
  }, null, 2));
} finally {
  await runtime.respan.flush();
}
