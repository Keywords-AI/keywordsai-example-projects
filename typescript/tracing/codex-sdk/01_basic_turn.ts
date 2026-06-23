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

const workflowName = "codex-sdk-ts-basic";
const respan = createRespan("codex-sdk-typescript-basic");

try {
  const result = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const codex = createCodex();
      const thread = codex.startThread(codexThreadOptions());
      return await withTimeout(
        thread.run("Reply with exactly one short sentence: Respan Codex SDK basic trace succeeded."),
        workflowName,
      );
    }),
  );

  logExampleResult(workflowName, {
    finalResponse: result.finalResponse,
    itemTypes: result.items.map((item) => item.type),
    usage: result.usage,
  });
} finally {
  await shutdownRespan(respan);
}
