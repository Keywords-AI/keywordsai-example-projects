import { logExampleResult, runADKExample } from "./_shared.js";

const workflowName = "Google ADK TS Hello World.workflow";
const result = await runADKExample({
  appName: "google-adk-typescript-examples",
  workflowName,
  mode: "hello",
  prompt: "Say hello from the Google ADK TypeScript example.",
});

logExampleResult(workflowName, {
  output: result.output,
  eventCount: result.events.length,
});
