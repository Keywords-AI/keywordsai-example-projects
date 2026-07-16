import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-tool");
runtime.options = {
  ...runtime.options,
  maxTurns: 2,
  allowedTools: ["Read", "Glob", "Grep"],
};

try {
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_tool.workflow",
      associationProperties: {
        run_id: runtime.runId,
        example: "claude-agent-sdk",
      },
    },
    async () =>
      await queryForResult(
        runtime,
        "List the filenames in the current directory. Keep the answer short.",
      ),
  );

  console.log(`subtype: ${String(result.subtype ?? "unknown")}`);
} finally {
  await shutdownRuntime(runtime);
}
