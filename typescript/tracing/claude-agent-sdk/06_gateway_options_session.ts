import { randomUUID } from "node:crypto";
import { SYSTEM_PROMPT_DYNAMIC_BOUNDARY } from "@anthropic-ai/claude-agent-sdk";
import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-options-session");

try {
  const sessionId = randomUUID();
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_options_session.workflow",
      associationProperties: {
        run_id: runtime.runId,
        session_id: sessionId,
        example: "claude-agent-sdk",
      },
    },
    async () =>
      await queryForResult(
        runtime,
        `Run ${runtime.runId}: answer in one concise sentence about session-scoped gateway tracing.`,
        {
          sessionId,
          persistSession: false,
          tools: [],
          permissionMode: "default",
          maxTurns: 1,
          includePartialMessages: true,
          systemPrompt: [
            "You are a concise observability assistant.",
            SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
            `Trace run id: ${runtime.runId}`,
          ],
          thinking: { type: "disabled" },
          effort: "low",
        },
      ),
  );

  console.log(JSON.stringify({
    subtype: String(result.subtype ?? "unknown"),
    sessionId,
  }, null, 2));
} finally {
  await shutdownRuntime(runtime);
}
