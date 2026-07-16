import { Agent } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-agent-as-tool");

try {
  const reviewerAgent = new Agent({
    name: "summary_reviewer_agent",
    instructions:
      "Review the supplied summary for clarity. Return one concise sentence with a score out of 10.",
    model: runtime.model,
  });

  const reviewSummaryTool = reviewerAgent.asTool({
    toolName: "review_summary",
    toolDescription: "Reviews a short observability summary before the final answer.",
    runConfig: {
      modelProvider: runtime.modelProvider,
    },
    runOptions: {
      maxTurns: 1,
    },
  });

  const coordinatorAgent = new Agent({
    name: "gateway_agent_tool_coordinator",
    instructions:
      "Draft a one-sentence summary, call review_summary, then return the improved final answer.",
    model: runtime.model,
    tools: [reviewSummaryTool],
  });

  const result = await withExampleTrace(
    runtime,
    "openai_agents_gateway_agent_as_tool.workflow",
    async () =>
      await runtime.runner.run(
        coordinatorAgent,
        `Run ${runtime.runId}: summarize why nested agent tools are useful for tracing.`,
        {
          maxTurns: 4,
        },
      ),
  );

  console.log(String(result.finalOutput ?? ""));
} finally {
  await shutdownRuntime(runtime);
}
