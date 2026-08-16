import { createAnthropicClient, createRuntime, runWithOpenInferenceWorkflow } from "./_runtime.js";

const workflowName = "openinference_anthropic_failure";
const { respan } = createRuntime();
let rejected = false;

try {
  await runWithOpenInferenceWorkflow(respan, workflowName, async () => {
    await createAnthropicClient().messages.create({
      model: process.env.RESPAN_ANTHROPIC_INVALID_MODEL || "respan-intentional-invalid-model",
      max_tokens: 20,
      messages: [
        { role: "user", content: "Exercise the expected Anthropic failure path." },
      ],
    });
  });
} catch (error) {
  rejected = true;
  const message = error instanceof Error ? error.message : String(error);
  console.log(JSON.stringify({ workflowName, expectedFailure: message }, null, 2));
} finally {
  await respan.shutdown();
}

if (!rejected) {
  throw new Error("Expected the unsupported Anthropic model request to fail.");
}
