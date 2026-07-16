import { logExampleResult, runCohereWorkflow } from "./_shared.js";

const workflowName = "cohere_ts_expected_error";

let message = "";
await runCohereWorkflow(workflowName, async ({ clientV2 }) => {
  try {
    await clientV2.chat({
      model: "force-error",
      messages: [{ role: "user", content: "Trigger the expected error path." }],
    });
  } catch (error) {
    message = error instanceof Error ? error.message : String(error);
  }
  return message;
});

logExampleResult(workflowName, {
  expectedError: true,
  message,
});
