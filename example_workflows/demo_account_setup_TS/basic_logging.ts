/**
 * Basic Logging Example
 *
 * This example demonstrates the basic logging functionality as shown in the
 * KeywordsAI quickstart guide.
 *
 * Quickstart guide: https://docs.keywordsai.co/get-started/quickstart/logging
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;

// Model configuration from environment variables
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

/**
 * Create a new log entry in Keywords AI.
 */
export async function createLog(options: CreateLogOptions): Promise<LogResponse> {
  const { model, inputMessages, outputMessage, customIdentifier, spanName, ...kwargs } = options;

  const url = `${BASE_URL}/request-logs/create`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    model,
    input: inputMessages,
    output: outputMessage,
  };

  if (customIdentifier) {
    payload.custom_identifier = customIdentifier;
  }
  if (spanName) {
    payload.span_name = spanName;
  }

  // Add any additional fields
  Object.assign(payload, kwargs);

  console.log("Creating log entry...");
  console.log(`  URL: ${url}`);
  console.log(`  Model: ${model}`);
  console.log(`  Input messages: ${inputMessages.length}`);
  if (customIdentifier) {
    console.log(`  Custom identifier: ${customIdentifier}`);
  }
  if (spanName) {
    console.log(`  Span name: ${spanName}`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: LogResponse = await response.json();
  console.log(`\n[OK] Log created successfully`);
  if (data.unique_id) {
    console.log(`  Log ID (unique_id): ${data.unique_id}`);
  }
  if (data.id) {
    console.log(`  Log ID: ${data.id}`);
  }
  if (data.trace_id) {
    console.log(`  Trace ID: ${data.trace_id}`);
  }

  return data;
}

async function main() {
  console.log("=".repeat(80));
  console.log("KeywordsAI Basic Logging Example");
  console.log("=".repeat(80));

  // Example 1: Simple log entry
  console.log("\n[Example 1] Creating a simple log entry");
  console.log("-".repeat(80));

  const logData1 = await createLog({
    model: DEFAULT_MODEL,
    inputMessages: [{ role: "user", content: "What is the capital of France?" }],
    outputMessage: {
      role: "assistant",
      content: "The capital of France is Paris.",
    },
  });

  // Example 2: Log with custom identifier
  console.log("\n[Example 2] Creating a log with custom identifier");
  console.log("-".repeat(80));

  const logData2 = await createLog({
    model: DEFAULT_MODEL_MINI,
    inputMessages: [{ role: "user", content: "Tell me a fun fact about space" }],
    outputMessage: {
      role: "assistant",
      content:
        "A day on Venus is longer than its year! Venus rotates so slowly that it takes longer to complete one rotation than to orbit the Sun once.",
    },
    customIdentifier: "space_fact_query_001",
  });

  // Example 3: Log with span name
  console.log("\n[Example 3] Creating a log with span name");
  console.log("-".repeat(80));

  const logData3 = await createLog({
    model: DEFAULT_MODEL_CLAUDE,
    inputMessages: [{ role: "user", content: "Explain quantum computing in simple terms" }],
    outputMessage: {
      role: "assistant",
      content:
        "Quantum computing uses quantum mechanical phenomena like superposition and entanglement to perform computations. Unlike classical bits that are either 0 or 1, quantum bits (qubits) can exist in multiple states simultaneously, allowing for parallel processing of information.",
    },
    spanName: "quantum_explanation",
  });

  // Example 4: Multi-turn conversation
  console.log("\n[Example 4] Creating a log for multi-turn conversation");
  console.log("-".repeat(80));

  const logData4 = await createLog({
    model: DEFAULT_MODEL,
    inputMessages: [
      { role: "user", content: "What's the weather like?" },
      {
        role: "assistant",
        content: "I don't have access to real-time weather data. Could you tell me your location?",
      },
      { role: "user", content: "San Francisco" },
    ],
    outputMessage: {
      role: "assistant",
      content:
        "I still can't access real-time weather, but I'd recommend checking a weather app or website like Weather.com for current conditions in San Francisco.",
    },
    customIdentifier: "weather_conversation_001",
    spanName: "weather_assistant",
  });

  console.log("\n" + "=".repeat(80));
  console.log("All examples completed successfully!");
  console.log("=".repeat(80));

  return {
    log_1: logData1,
    log_2: logData2,
    log_3: logData3,
    log_4: logData4,
  };
}

// Run main only if this is the entry point (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
