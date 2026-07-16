import { logExampleResult, runADKExample } from "./_shared.js";

const workflowName = "Google ADK TS Streaming Attributes.workflow";
const result = await runADKExample({
  appName: "google-adk-typescript-examples",
  workflowName,
  mode: "stream",
  prompt: "Stream a short response and keep Respan attributes propagated.",
  streaming: true,
});

logExampleResult(workflowName, {
  output: result.output,
  eventCount: result.events.length,
});
