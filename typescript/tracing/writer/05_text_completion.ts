import {
  createRespan,
  createWriterClient,
  DEFAULT_COMPLETION_MODEL,
  logExampleResult,
  runWithWriterWorkflow,
  shutdownRespan,
  withTimeout,
} from "./_shared.js";

const workflowName = "writer.text_completion.workflow";
const respan = createRespan();
const writer = createWriterClient();

try {
  const completion = await withTimeout(
    runWithWriterWorkflow(respan, workflowName, async () => {
      return await writer.completions.create({
        model: DEFAULT_COMPLETION_MODEL,
        prompt: "Write one sentence about observability traces.",
        max_tokens: 48,
        temperature: 0.1,
      });
    }),
    workflowName,
  );

  logExampleResult(workflowName, {
    expected: "one text completion span",
    actual: completion.choices[0]?.text,
    model: completion.model,
  });
} finally {
  await shutdownRespan(respan);
}
