/**
 * Basic Gateway - Route Claude Agent SDK calls through Respan gateway.
 *
 * Run:
 *   npx tsx basic_gateway.ts
 */

import "dotenv/config";
import { API_KEY, BASE_URL, ClaudeAgentSDK } from "./_runtime";

const gatewayUrl = `${BASE_URL}/anthropic`;
let sessionId: string | undefined;

const stream = await ClaudeAgentSDK.query({
  prompt: "Reply with exactly: gateway_ok",
  options: {
    permissionMode: "bypassPermissions",
    maxTurns: 1,
    env: { ...process.env, ANTHROPIC_BASE_URL: gatewayUrl, ANTHROPIC_AUTH_TOKEN: API_KEY, ANTHROPIC_API_KEY: API_KEY },
  },
});

for await (const message of stream) {
  if (message.type === "system") sessionId = message.session_id;
  console.log(`  ${message.type}`);
}

console.log(`\nSession: ${sessionId}`);
console.log("View trace at: https://platform.respan.ai/platform/traces");
