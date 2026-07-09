/**
 * Tool Use via Gateway - Run agent with tools, routed through Respan gateway.
 *
 * Run:
 *   npx tsx tool_use_gateway.ts
 */

import "dotenv/config";
import { API_KEY, BASE_URL, ClaudeAgentSDK } from "./_runtime";

const gatewayUrl = `${BASE_URL}/anthropic`;
let sessionId: string | undefined;

const stream = await ClaudeAgentSDK.query({
  prompt: "List the TypeScript files in the current directory. Just show filenames.",
  options: {
    permissionMode: "bypassPermissions",
    maxTurns: 3,
    allowedTools: ["Read", "Glob", "Grep"],
    env: { ...process.env, ANTHROPIC_BASE_URL: gatewayUrl, ANTHROPIC_AUTH_TOKEN: API_KEY, ANTHROPIC_API_KEY: API_KEY },
  },
});

for await (const message of stream) {
  if (message.type === "system") sessionId = message.session_id;
  console.log(`  ${message.type}`);
}

console.log(`\nSession: ${sessionId}`);
console.log("Check Respan traces to see tool spans (Read, Glob, etc.)");
