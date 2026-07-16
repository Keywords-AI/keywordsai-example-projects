import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-basic");

try {
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_basic.workflow",
      associationProperties: {
        run_id: runtime.runId,
        example: "claude-agent-sdk",
      },
    },
    async () => await queryForResult(runtime, "Reply with exactly: claude_gateway_ok"),
  );

  console.log(`subtype: ${String(result.subtype ?? "unknown")}`);
} finally {
  await shutdownRuntime(runtime);
}
