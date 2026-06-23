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

const workflowName = "codex-sdk-ts-streaming";
const respan = createRespan("codex-sdk-typescript-streaming");

try {
  const details = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const codex = createCodex();
      const thread = codex.startThread(codexThreadOptions());
      const streamed = await thread.runStreamed(
        "Run `pwd` if useful, then answer with one short sentence that streaming worked.",
      );
      const eventTypes: string[] = [];
      const itemTypes: string[] = [];
      let finalResponse = "";

      await withTimeout(
        (async () => {
          for await (const event of streamed.events) {
            eventTypes.push(event.type);
            if ("item" in event) {
              itemTypes.push(event.item.type);
              if (event.type === "item.completed" && event.item.type === "agent_message") {
                finalResponse = event.item.text;
              }
            }
          }
        })(),
        workflowName,
      );

      return { eventTypes, itemTypes, finalResponse };
    }),
  );

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
