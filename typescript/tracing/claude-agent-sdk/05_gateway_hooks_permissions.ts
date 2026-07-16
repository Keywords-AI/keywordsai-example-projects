import assert from "node:assert/strict";
import { rm } from "node:fs/promises";
import type { HookInput } from "@anthropic-ai/claude-agent-sdk";
import { createRuntime, queryForResult, shutdownRuntime } from "./_runtime.js";

const runtime = await createRuntime("claude-agent-sdk-gateway-hooks-permissions");
const tempPermissionPath = "/tmp/respan_claude_agent_sdk_permission.txt";
const permissionDecisions: string[] = [];
const hookEvents: string[] = [];

try {
  const result = await runtime.respan.withWorkflow(
    {
      name: "claude_agent_sdk_gateway_hooks_permissions.workflow",
      associationProperties: {
        run_id: runtime.runId,
        example: "claude-agent-sdk",
      },
    },
    async () =>
      await queryForResult(
        runtime,
        `Use Bash exactly once with command "printf respan > ${tempPermissionPath}", then report done.`,
        {
          maxTurns: 4,
          tools: ["Bash"],
          settingSources: [],
          permissionMode: "default",
          allowDangerouslySkipPermissions: false,
          includeHookEvents: true,
          hooks: {
            PreToolUse: [
              {
                hooks: [
                  async (input: HookInput) => {
                    hookEvents.push(String(input.hook_event_name));
                    return {
                      continue: true,
                      hookSpecificOutput: {
                        hookEventName: "PreToolUse",
                        additionalContext: "Permission callback should decide this tool call.",
                      },
                    };
                  },
                ],
              },
            ],
            PostToolUse: [
              {
                hooks: [
                  async (input: HookInput) => {
                    hookEvents.push(String(input.hook_event_name));
                    return {
                      continue: true,
                      hookSpecificOutput: {
                        hookEventName: "PostToolUse",
                        additionalContext: "Read tool completed in the hooks example.",
                      },
                    };
                  },
                ],
              },
            ],
          },
          canUseTool: async (toolName: string) => {
            permissionDecisions.push(toolName);
            return {
              behavior: "allow",
              updatedInput: {},
              decisionClassification: "user_temporary",
            };
          },
        },
      ),
  );

  assert.ok(hookEvents.includes("PreToolUse"));
  assert.ok(hookEvents.includes("PostToolUse"));
  assert.ok(permissionDecisions.includes("Bash"));

  console.log(JSON.stringify({
    subtype: String(result.subtype ?? "unknown"),
    hookEvents,
    permissionDecisions,
  }, null, 2));
} finally {
  await rm(tempPermissionPath, { force: true });
  await shutdownRuntime(runtime);
}
