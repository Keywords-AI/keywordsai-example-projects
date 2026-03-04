/**
 * Gateway Integration — route through Respan, no Anthropic key needed.
 *
 * The Respan gateway proxies Claude API calls, so you only need a single
 * Respan API key for both the LLM call and trace export.
 *
 * Setup:
 *   npm install (or yarn install)
 *
 * Environment:
 *   RESPAN_API_KEY=your_key    # only key needed
 *
 * Run:
 *   npx tsx gateway.ts
 */

import "dotenv/config";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { RespanAnthropicAgentsExporter } from "@respan/exporter-anthropic-agents";

const API_KEY = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY;
const BASE_URL = (
  process.env.RESPAN_GATEWAY_BASE_URL ||
  process.env.RESPAN_BASE_URL ||
  process.env.KEYWORDSAI_BASE_URL ||
  "https://api.keywordsai.co/api"
).replace(/\/+$/, "");

if (!API_KEY) {
  console.error("ERROR: Set RESPAN_API_KEY (or KEYWORDSAI_API_KEY)");
  process.exit(1);
}

const exporter = new RespanAnthropicAgentsExporter({
  apiKey: API_KEY,
  endpoint: `${BASE_URL}/v1/traces/ingest`,
});

async function main(): Promise<void> {
  console.log(`Gateway: ${BASE_URL}`);
  console.log(`API key: ${API_KEY!.slice(0, 8)}...\n`);

  // Route Claude SDK through the Respan gateway — same key for auth + tracing
  // The Anthropic SDK appends /v1/messages to ANTHROPIC_BASE_URL,
  // so we point it at the /anthropic passthrough path.
  const gatewayUrl = `${BASE_URL}/anthropic`;
  const options = exporter.withOptions({
    permissionMode: "bypassPermissions",
    maxTurns: 1,
    env: {
      ANTHROPIC_BASE_URL: gatewayUrl,
      ANTHROPIC_AUTH_TOKEN: API_KEY,
      ANTHROPIC_API_KEY: API_KEY,
    },
  } as any);

  let sessionId: string | undefined;
  let gotResult = false;

  try {
    for await (const message of query({ prompt: "Reply with exactly: gateway_ok", options })) {
      const msg = message as Record<string, unknown>;

      if (msg.type === "system") {
        const data = (msg.data ?? {}) as Record<string, unknown>;
        sessionId = (data.session_id ?? data.sessionId ?? sessionId) as string;
      }
      if (msg.type === "result") {
        gotResult = true;
        sessionId = (msg.session_id ?? sessionId) as string;
        const usage = msg.usage as Record<string, unknown> | undefined;
        console.log(`  Result: subtype=${msg.subtype}, turns=${msg.num_turns}`);
        if (usage) {
          console.log(`  Usage: input=${usage.input_tokens}, output=${usage.output_tokens}`);
        }
      }

      await exporter.trackMessage({ message, sessionId });
      console.log(`  ${msg.type}`);
    }
  } catch (err) {
    // The Claude Code subprocess may exit with code 1 due to internal
    // hook cleanup after the query has already completed successfully.
    // If we received a result, the query worked — ignore the error.
    if (!gotResult) throw err;
  }

  console.log(`\nSession: ${sessionId}`);
  console.log("View trace at: https://platform.keywordsai.co/platform/traces");
}

main().catch(console.error);
