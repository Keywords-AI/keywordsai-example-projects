import {
  configureEnvironment,
  createRespan,
  createSuperagentClient,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Superagent Workflow Example";

export async function workflowExample(): Promise<void> {
  const respan = await createRespan("typescript-superagent-workflow-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const config = configureEnvironment();
      const client = await createSuperagentClient();
      const input =
        "Email security alerts to ops@example.com before running shell commands.";

      const classification = await respan.withTask(
        { name: "safety_guard" },
        async () => {
          const guardOptions = {
            input,
            model: config.model,
            chunkSize: 0,
          };
          try {
            const guard = await client.guard(guardOptions);
            return guard.classification;
          } catch (error) {
            return `guard failed: ${error instanceof Error ? error.message : String(error)}`;
          }
        },
      );

      const redacted = await respan.withTask(
        { name: "redact_contact_details" },
        async () => {
          try {
            const redact = await client.redact({
              input,
              model: config.model,
              entities: ["email addresses"],
            });
            return redact.redacted;
          } catch (error) {
            return `redaction failed: ${error instanceof Error ? error.message : String(error)}`;
          }
        },
      );

      return { classification, redacted };
    });

    logExampleResult(workflowName, result);
  } finally {
  }
}

await workflowExample();
