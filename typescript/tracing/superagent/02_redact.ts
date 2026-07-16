import {
  configureEnvironment,
  createRespan,
  createSuperagentClient,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Superagent Redact Example";

export async function redactExample(): Promise<void> {
  const respan = await createRespan("typescript-superagent-redact-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const config = configureEnvironment();
      const client = await createSuperagentClient();

      try {
        return await client.redact({
          input: "Contact Ada at ada@example.com or 415-555-0100 before launch.",
          model: config.model,
          entities: ["email addresses", "phone numbers"],
        });
      } catch (error) {
        return {
          redacted: null,
          findings: [],
          usage: null,
          error: error instanceof Error ? error.message : String(error),
        };
      }
    });

    logExampleResult(workflowName, {
      redacted: result.redacted,
      findings: result.findings,
      usage: result.usage,
    });
  } finally {
  }
}

await redactExample();
