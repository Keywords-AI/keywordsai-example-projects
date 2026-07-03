import { Respan } from "@respan/respan";
import { loadAutoInstrumentExampleEnv } from "./_env.js";

const EXAMPLE_SET = "typescript/tracing/auto-instrument-direct-llm";
const WORKFLOW_NAME = "ts_auto_instrument_openai_gateway";

function runId(): string {
  return process.env.RESPAN_EXAMPLE_RUN_ID || `ts-auto-direct-llm-${Date.now()}`;
}

function printInstrumentationStatus(respan: Respan): void {
  const status = respan.getInstrumentationStatus().map((entry) => ({
    id: entry.id,
    status: entry.status,
    package: entry.instrumentationPackage,
    reason: entry.reason ?? "",
  }));
  console.log("Auto-instrumentation status:");
  console.table(status);
}

async function main(): Promise<void> {
  const env = loadAutoInstrumentExampleEnv();
  const currentRunId = runId();

  const respan = new Respan({
    apiKey: env.respanApiKey,
    baseURL: env.respanBaseURL,
    appName: "respan-ts-auto-instrument-direct-llm-example",
    logLevel: "error",
    silenceInitializationMessage: true,
  });

  await respan.initialize();
  printInstrumentationStatus(respan);

  const { default: OpenAI } = await import("openai");
  const openai = new OpenAI({
    apiKey: env.gatewayApiKey,
    baseURL: env.gatewayBaseURL,
  });

  try {
    const answer = await respan.propagateAttributes(
      {
        trace_group_identifier: currentRunId,
        metadata: {
          example_set: EXAMPLE_SET,
          run_id: currentRunId,
          gateway_base_url: env.gatewayBaseURL,
          auto_instrument: "direct-llm",
        },
      },
      () =>
        respan.withWorkflow(
          {
            name: WORKFLOW_NAME,
            associationProperties: {
              example_set: EXAMPLE_SET,
              language: "typescript",
              sdk: "openai",
              gateway: "respan",
              run_id: currentRunId,
            },
          },
          async () => {
            const completion = await openai.chat.completions.create({
              model: env.model,
              messages: [
                {
                  role: "system",
                  content: "You are a concise tracing test assistant.",
                },
                {
                  role: "user",
                  content:
                    "Reply with one short sentence that includes the phrase auto instrumentation.",
                },
              ],
            });

            return completion.choices[0]?.message?.content ?? "";
          },
        ),
    );

    console.log(`run_id: ${currentRunId}`);
    console.log(`model: ${env.model}`);
    console.log(`answer: ${answer}`);
  } finally {
    await respan.shutdown();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
