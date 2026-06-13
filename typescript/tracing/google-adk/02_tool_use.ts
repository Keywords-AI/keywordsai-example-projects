import { logExampleResult, runADKExample } from "./_shared.js";

const workflowName = "Google ADK TS Tool Use.workflow";
const result = await runADKExample({
  appName: "google-adk-typescript-examples",
  workflowName,
  mode: "tool",
  prompt: "Use the weather tool to check Tokyo.",
});

logExampleResult(workflowName, {
  output: result.output,
  eventCount: result.events.length,
});
