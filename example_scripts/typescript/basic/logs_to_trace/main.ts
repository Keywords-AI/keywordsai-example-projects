#!/usr/bin/env npx tsx
/**
 * Trace Log Demo
 *
 * This script demonstrates how to send trace logs to KeywordsAI while avoiding ID collisions.
 *
 * Files:
 * - trace_logs.json: Sample trace data - clean, accurate payload format exactly as it would appear in the payload
 * - utils.ts: Processing utilities that shift timestamps and remap IDs
 * - main.ts: This demo script (2 lines of logic)
 *
 * How it works:
 * 1. generateTraceData() takes the sample logs and shifts timestamps to current time
 * 2. It remaps trace_unique_id and span_unique_id to prevent aggregation onto wrong traces
 * 3. Data shape remains unchanged - only timestamps and IDs are modified
 * 4. Processed logs are sent directly to KeywordsAI traces endpoint
 *
 * Usage:
 *   cd example_scripts/typescript
 *   npx tsx basic/logs_to_trace/main.ts
 */

import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { config } from "dotenv";
import { generateTraceData } from "./utils.js";

// Load environment variables
config({ override: true });

// Get the directory of the current file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read the trace logs from JSON file
const traceLogsPath = join(__dirname, "trace_logs.json");
const traceLogsData = JSON.parse(readFileSync(traceLogsPath, "utf-8"));

// Process the logs with current timestamp
const processedLogs = generateTraceData(traceLogsData, new Date());

// Send to KeywordsAI traces endpoint
const baseUrl = process.env.KEYWORDSAI_BASE_URL;
const apiKey = process.env.KEYWORDSAI_API_KEY;

if (!baseUrl || !apiKey) {
  console.error(
    "Error: KEYWORDSAI_BASE_URL and KEYWORDSAI_API_KEY environment variables are required"
  );
  process.exit(1);
}

const response = await fetch(`${baseUrl}/v1/traces/ingest`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
  body: JSON.stringify(processedLogs),
});

console.log(
  `Status: ${response.status}, Trace ID: ${processedLogs[0]?.trace_unique_id}`
);
