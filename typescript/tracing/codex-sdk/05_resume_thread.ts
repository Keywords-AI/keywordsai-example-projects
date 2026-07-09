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

const workflowName = "codex-sdk-ts-resume-thread";
const respan = createRespan("codex-sdk-typescript-resume-thread");

try {
  const details = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const codex = createCodex();
      const thread = codex.startThread(codexThreadOptions());
      const first = await withTimeout(
        thread.run("Remember the word respan. Reply with: remembered."),
        `${workflowName}-first`,
      );
      const threadId = thread.id;
      if (!threadId) throw new Error("Codex thread did not expose an id after first turn.");

      const resumedThread = codex.resumeThread(threadId, codexThreadOptions());
      const second = await withTimeout(
        resumedThread.run("What word did I ask you to remember? Reply with that word only."),
        `${workflowName}-second`,
      );

      return {
        firstResponse: first.finalResponse,
        secondResponse: second.finalResponse,
        threadId,
      };
    }),
  );

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
