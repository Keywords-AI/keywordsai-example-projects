import { Agent } from "@mastra/core/agent";
import { createGatewayModel, createRuntime, EXAMPLE_RUN_ID, getTraceWorkflowName, runWithRespanWorkflow } from "./_shared.js";

const workflowName = "Mastra Streaming Example";
const streamingAgent = new Agent({
  id: "mastra-streaming-agent",
  name: "Mastra Streaming Agent",
  instructions: "Describe Respan as an AI tracing and observability product for Mastra TypeScript applications. Reply in exactly two short sentences.",
  model: createGatewayModel(),
});

const { mastra, respan } = createRuntime({ streamingAgent });

const text = await runWithRespanWorkflow(respan, workflowName, async () => {
  const agent = mastra.getAgent("streamingAgent");
  const stream = await agent.stream("Describe Respan tracing for a Mastra TypeScript agent application.");
  let output = "";
  for await (const chunk of stream.textStream) {
    output += chunk;
  }
  return output;
});

console.log(JSON.stringify({ workflowName: getTraceWorkflowName(workflowName), runId: EXAMPLE_RUN_ID, text }, null, 2));
