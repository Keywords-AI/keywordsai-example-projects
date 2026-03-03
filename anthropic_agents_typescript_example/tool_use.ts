/**
 * Tool Use — trace agent tool calls through Respan.
 *
 * Runs a query that uses Claude Code's built-in tools (Read, Glob, Grep),
 * then exports the full trace including tool spans.
 *
 * Setup:
 *   npm install (or yarn install)
 *
 * Run:
 *   npx tsx tool_use.ts
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
  console.log("Running query with tools (Read, Glob, Grep)...\n");

  const options = exporter.withOptions({
    permissionMode: "bypassPermissions",
    maxTurns: 3,
    allowedTools: ["Read", "Glob", "Grep"],
  } as any);

  let sessionId: string | undefined;

  for await (const message of query({
    prompt: "List the files in the current directory. Just show filenames.",
    options,
  })) {
    const msg = message as Record<string, unknown>;

    if (msg.type === "system") {
      const data = (msg.data ?? {}) as Record<string, unknown>;
      sessionId = (data.session_id ?? data.sessionId ?? sessionId) as string;
    }
    if (msg.type === "result") {
      sessionId = (msg.session_id ?? sessionId) as string;
      console.log(`  Result: subtype=${msg.subtype}, turns=${msg.num_turns}`);
    }

    await exporter.trackMessage({ message, sessionId });
    console.log(`  ${msg.type}`);
  }

  console.log(`\nSession: ${sessionId}`);
  console.log("Check Respan traces to see tool spans (Read, Glob, etc.)");
}

main().catch(console.error);
