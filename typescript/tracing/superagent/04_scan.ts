import {
  configureEnvironment,
  createRespan,
  createSuperagentClient,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Superagent Scan Example";

export async function scanExample(): Promise<void> {
  const respan = await createRespan("typescript-superagent-scan-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      if (!process.env.DAYTONA_API_KEY) {
        return {
          skipped: true,
          reason: "DAYTONA_API_KEY is not set; skipping live scan example.",
        };
      }

      const config = configureEnvironment();
      const client = await createSuperagentClient();
      try {
        const scan = await client.scan({
          repo: "https://github.com/respanai/respan-example-projects",
          model: config.model,
        });

        return {
          skipped: false,
          result: scan.result.slice(0, 500),
          usage: scan.usage,
        };
      } catch (error) {
        return {
          skipped: false,
          error: error instanceof Error ? error.message : String(error),
        };
      }
    });

    logExampleResult(workflowName, result);
  } finally {
  }
}

await scanExample();
