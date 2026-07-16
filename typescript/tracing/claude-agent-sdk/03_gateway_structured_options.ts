import type { HookInput } from "@anthropic-ai/claude-agent-sdk";
import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-structured-options");
const hookEvents: string[] = [];

const outputSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    runId: { type: "string" },
    mode: { type: "string" },
    answer: { type: "string" },
  },
  required: ["runId", "mode", "answer"],
};

try {
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_structured_options.workflow",
      associationProperties: {
        run_id: runtime.runId,
        example: "claude-agent-sdk",
      },
    },
    async () =>
      await queryForResult(
        runtime,
        `Run ${runtime.runId}: return structured JSON describing one Respan gateway benefit.`,
        {
          agent: "respan-observer",
          agents: {
            "respan-observer": {
              description: "Produces short structured observability answers.",
              prompt:
                "You answer with compact JSON that matches the requested schema and does not use tools.",
              tools: [],
              model: "sonnet",
              maxTurns: 1,
            },
          },
          tools: [],
          permissionMode: "default",
          maxTurns: 1,
          includeHookEvents: true,
          includePartialMessages: true,
          outputFormat: {
            type: "json_schema",
            schema: outputSchema,
          },
          hooks: {
            UserPromptSubmit: [
              {
                hooks: [
                  async (input: HookInput) => {
                    hookEvents.push(String(input.hook_event_name));
                    return {
                      continue: true,
                      hookSpecificOutput: {
                        hookEventName: "UserPromptSubmit",
                        additionalContext: `trace run id: ${runtime.runId}`,
                      },
                    };
                  },
                ],
              },
            ],
          },
        },
      ),
  );

  console.log(JSON.stringify({
    subtype: String(result.subtype ?? "unknown"),
    hookEvents,
  }, null, 2));
} finally {
  await shutdownRuntime(runtime);
}
