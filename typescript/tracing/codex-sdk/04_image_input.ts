import {
  codexThreadOptions,
  createCodex,
  createDemoImage,
  createRespan,
  logExampleResult,
  runWithCodexWorkflow,
  shutdownRespan,
  withCodexRetries,
  withTimeout,
} from "./_shared.js";

const workflowName = "codex-sdk-ts-image-input";
const respan = createRespan("codex-sdk-typescript-image-input");

try {
  const result = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const imagePath = await createDemoImage();
      const codex = createCodex();
      const thread = codex.startThread(codexThreadOptions());
      return await withTimeout(
        thread.run([
          { type: "text", text: "Describe this tiny image in five words or fewer." },
          { type: "local_image", path: imagePath },
        ]),
        workflowName,
      );
    }),
  );

  logExampleResult(workflowName, {
    finalResponse: result.finalResponse,
    itemTypes: result.items.map((item) => item.type),
  });
} finally {
  await shutdownRespan(respan);
}
