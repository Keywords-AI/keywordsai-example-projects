/**
 * Hello World — Anthropic Agent SDK + Respan tracing.
 *
 * The simplest possible example: ask Claude a question, see the trace in Respan.
 *
 * Setup:
 *   npm install (or yarn install)
 *
 * Run:
 *   npx tsx hello_world.ts
 */

import "dotenv/config";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { RespanAnthropicAgentsExporter } from "@respan/exporter-anthropic-agents";

const API_KEY = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY;
const BASE_URL = process.env.RESPAN_BASE_URL || process.env.KEYWORDSAI_BASE_URL;

const exporter = new RespanAnthropicAgentsExporter({
  apiKey: API_KEY ?? undefined,
  endpoint: BASE_URL ? `${BASE_URL.replace(/\/+$/, "")}/v1/traces/ingest` : undefined,
});

async function main(): Promise<void> {
  console.log("Asking Claude a question...\n");

  // Attach exporter hooks to SDK options
  const options = exporter.withOptions({
    permissionMode: "bypassPermissions",
    maxTurns: 1,
  });

  let sessionId: string | undefined;

  for await (const message of query({ prompt: "What is 2 + 2? Reply in one word.", options })) {
    const msg = message as Record<string, unknown>;

    // Track session ID
    if (msg.type === "system") {
      const data = (msg.data ?? {}) as Record<string, unknown>;
      sessionId = (data.session_id ?? data.sessionId ?? sessionId) as string;
    }
    if (msg.type === "result") {
      sessionId = (msg.session_id ?? sessionId) as string;
      console.log(`  Result: subtype=${msg.subtype}, turns=${msg.num_turns}`);
    }

    // Export each message to Respan
    await exporter.trackMessage({ message, sessionId });
    console.log(`  ${msg.type}`);
  }

  console.log(`\nSession: ${sessionId}`);
  console.log("View trace at: https://platform.keywordsai.co/traces");
}

main().catch(console.error);
