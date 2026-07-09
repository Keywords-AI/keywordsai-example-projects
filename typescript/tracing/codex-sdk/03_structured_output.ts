import {
  codexThreadOptions,
  createCodex,
  createRespan,
  logExampleResult,
  runWithCodexWorkflow,
  shutdownRespan,
  withCodexRetries,
  withTimeout,
} from "./_shared.js";

const workflowName = "codex-sdk-ts-structured-output";
const respan = createRespan("codex-sdk-typescript-structured-output");

const outputSchema = {
  type: "object",
  properties: {
    summary: { type: "string" },
    status: { type: "string", enum: ["ok"] },
  },
  required: ["summary", "status"],
  additionalProperties: false,
} as const;

try {
  const result = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const codex = createCodex();
      const thread = codex.startThread(codexThreadOptions());
      return await withTimeout(
        thread.run("Return JSON only. summary must say structured Codex output is traced; status must be ok.", {
          outputSchema,
        }),
        workflowName,
      );
    }),
  );

  logExampleResult(workflowName, {
    finalResponse: result.finalResponse,
    usage: result.usage,
  });
} finally {
  await shutdownRespan(respan);
}
