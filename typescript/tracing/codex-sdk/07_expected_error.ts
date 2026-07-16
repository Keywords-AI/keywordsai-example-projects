import {
  codexThreadOptions,
  createCodex,
  createRespan,
  logExampleResult,
  runWithCodexWorkflow,
  shutdownRespan,
} from "./_shared.js";

const workflowName = "codex-sdk-ts-expected-error";
const respan = createRespan("codex-sdk-typescript-expected-error");

try {
  const details = await runWithCodexWorkflow(respan, workflowName, async () => {
    const codex = createCodex({ codexPathOverride: "/tmp/respan-missing-codex-binary" });
    const thread = codex.startThread(codexThreadOptions());
    try {
      await thread.run("This request is expected to fail before Codex starts.");
      return { expectedError: false };
    } catch (error) {
      return {
        expectedError: true,
        message: error instanceof Error ? error.message : String(error),
      };
    }
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
