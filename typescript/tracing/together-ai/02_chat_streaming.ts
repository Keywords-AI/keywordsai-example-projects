import {
  MODELS,
  captureFeature,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
  withTogetherRetries,
} from "./_shared.js";

const workflowName = "together-ai-ts-chat-streaming";
const respan = createRespan("together-ai-typescript-chat-streaming");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    return await captureFeature(workflowName, async () => {
      const stream = await withTogetherRetries(workflowName, async () =>
        await client.chat.completions.create({
          model: MODELS.chat,
          messages: [{ role: "user", content: "Stream five words about tracing." }],
          max_tokens: 40,
          temperature: 0,
          stream: true,
        }),
      );

      let text = "";
      let chunks = 0;
      for await (const chunk of stream) {
        chunks += 1;
        text += chunk.choices?.[0]?.delta?.content ?? "";
      }
      return { model: MODELS.chat, chunks, text };
    });
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
