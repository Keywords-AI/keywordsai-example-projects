import {
  MODELS,
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
  summarizeChatCompletion,
  withTogetherRetries,
} from "./_shared.js";

const workflowName = "together-ai-ts-chat-completion";
const respan = createRespan("together-ai-typescript-chat");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    return await captureFeature(workflowName, async () => {
      const response = await withTogetherRetries(workflowName, async () =>
        await client.chat.completions.create({
          model: MODELS.chat,
          messages: [
            { role: "system", content: "Answer in one concise sentence." },
            { role: "user", content: "Say that Respan Together AI chat tracing succeeded." },
          ],
          max_tokens: 64,
          temperature: 0,
        }),
      );
      return summarizeChatCompletion(response);
    });
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
