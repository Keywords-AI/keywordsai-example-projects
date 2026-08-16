/** Anthropic SDK — Chat completion with Respan tracing via OpenInference. */

import { createAnthropicClient, createRuntime, runWithOpenInferenceWorkflow } from "./_runtime.js";

const workflowName = "openinference_anthropic_supported";
const { respan } = createRuntime();

try {
  const output = await runWithOpenInferenceWorkflow(respan, workflowName, async () => {
    const message = await createAnthropicClient().messages.create({
      model: process.env.RESPAN_ANTHROPIC_MODEL || "claude-sonnet-4-5-20250929",
      max_tokens: 100,
      messages: [
        { role: "user", content: "Write a haiku about recursion in programming." },
      ],
    });

    return message.content
      .map((block) => (block.type === "text" ? block.text : ""))
      .filter(Boolean)
      .join("\n");
  });
  console.log(JSON.stringify({ workflowName, output }, null, 2));
} finally {
  await respan.shutdown();
}
