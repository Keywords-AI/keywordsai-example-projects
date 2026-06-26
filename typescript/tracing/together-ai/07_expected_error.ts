import {
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
} from "./_shared.js";

const workflowName = "together-ai-ts-expected-error";
const respan = createRespan("together-ai-typescript-expected-error");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    const result = await captureFeature(workflowName, async () =>
      await client.chat.completions.create({
        model: "respan/nonexistent-together-model",
        messages: [{ role: "user", content: "This request is expected to fail." }],
        max_tokens: 8,
      }),
    );
    return { expectedError: !result.ok, result };
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
