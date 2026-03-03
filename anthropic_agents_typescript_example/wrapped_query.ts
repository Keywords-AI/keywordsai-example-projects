/**
 * Wrapped Query — the simplest integration pattern.
 *
 * Uses exporter.query() which handles hooks + tracking automatically.
 * One line to instrument, zero boilerplate.
 *
 * Setup:
 *   npm install (or yarn install)
 *
 * Run:
 *   npx tsx wrapped_query.ts
 */

import "dotenv/config";
import { RespanAnthropicAgentsExporter } from "@respan/exporter-anthropic-agents";

const API_KEY = process.env.RESPAN_API_KEY || process.env.KEYWORDSAI_API_KEY;
const BASE_URL = process.env.RESPAN_BASE_URL || process.env.KEYWORDSAI_BASE_URL;

const exporter = new RespanAnthropicAgentsExporter({
  apiKey: API_KEY ?? undefined,
  endpoint: BASE_URL ? `${BASE_URL.replace(/\/+$/, "")}/v1/traces/ingest` : undefined,
});

async function main(): Promise<void> {
  console.log("Running wrapped query — exporter handles everything...\n");

  const messageTypes: string[] = [];

  for await (const message of exporter.query({
    prompt: "Name three primary colors. One word each, comma separated.",
    options: {
      permissionMode: "bypassPermissions",
      maxTurns: 1,
    } as any,
  })) {
    const msg = message as Record<string, unknown>;
    const msgType = String(msg.type ?? "unknown");
    messageTypes.push(msgType);
    console.log(`  ${msgType}`);
  }

  console.log(`\nMessage flow: ${messageTypes.join(" -> ")}`);
  console.log("All traces exported automatically via exporter.query()");
}

main().catch(console.error);
