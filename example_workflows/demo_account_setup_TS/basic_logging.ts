/**
 * Basic Logging Example
 * Documentation: https://docs.keywordsai.co/get-started/quickstart/logging
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;
const DEFAULT_MODEL = process.env.DEFAULT_MODEL || "gpt-4o";
const DEFAULT_MODEL_MINI = process.env.DEFAULT_MODEL_MINI || "gpt-4o-mini";
const DEFAULT_MODEL_CLAUDE = process.env.DEFAULT_MODEL_CLAUDE || "claude-3-5-sonnet-20241022";

interface Message {
  role: string;
  content: string;
}

interface CreateLogOptions {
  model: string;
  inputMessages: Message[];
  outputMessage: Message;
  customIdentifier?: string;
  spanName?: string;
  [key: string]: unknown;
}

interface LogResponse {
  id?: string;
  unique_id?: string;
  trace_id?: string;
  [key: string]: unknown;
}

export async function createLog(options: CreateLogOptions): Promise<LogResponse> {
  const { model, inputMessages, outputMessage, customIdentifier, spanName, ...kwargs } = options;

  const url = `${BASE_URL}/request-logs/create`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = { model, input: inputMessages, output: outputMessage };
  if (customIdentifier) payload.custom_identifier = customIdentifier;
  if (spanName) payload.span_name = spanName;
  Object.assign(payload, kwargs);

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: LogResponse = await response.json();
  console.log(`[OK] Log created: ${data.unique_id || data.id}`);
  return data;
}

async function main() {
  console.log("Basic Logging Example\n");

  // Example 1: Simple log
  console.log("[1] Simple log");
  await createLog({
    model: DEFAULT_MODEL,
    inputMessages: [{ role: "user", content: "What is the capital of France?" }],
    outputMessage: { role: "assistant", content: "The capital of France is Paris." },
  });

  // Example 2: Log with custom identifier
  console.log("\n[2] Log with custom identifier");
  await createLog({
    model: DEFAULT_MODEL_MINI,
    inputMessages: [{ role: "user", content: "Tell me a fun fact about space" }],
    outputMessage: {
      role: "assistant",
      content: "A day on Venus is longer than its year!",
    },
    customIdentifier: "space_fact_query_001",
  });

  // Example 3: Log with span name
  console.log("\n[3] Log with span name");
  await createLog({
    model: DEFAULT_MODEL_CLAUDE,
    inputMessages: [{ role: "user", content: "Explain quantum computing in simple terms" }],
    outputMessage: {
      role: "assistant",
      content: "Quantum computing uses quantum mechanical phenomena to perform computations.",
    },
    spanName: "quantum_explanation",
  });

  // Example 4: Multi-turn conversation
  console.log("\n[4] Multi-turn conversation");
  await createLog({
    model: DEFAULT_MODEL,
    inputMessages: [
      { role: "user", content: "What's the weather like?" },
      { role: "assistant", content: "I don't have access to real-time weather data." },
      { role: "user", content: "San Francisco" },
    ],
    outputMessage: {
      role: "assistant",
      content: "I'd recommend checking a weather app for San Francisco.",
    },
    customIdentifier: "weather_conversation_001",
    spanName: "weather_assistant",
  });

  console.log("\nDone.");
}

const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
