import { Agent } from "@mastra/core/agent";
import { createGatewayModel, createRuntime, EXAMPLE_RUN_ID, getTraceWorkflowName, runWithRespanWorkflow } from "./_shared.js";

const workflowName = "Mastra Basic Example";
const assistantAgent = new Agent({
  id: "mastra-basic-assistant",
  name: "Mastra Basic Assistant",
  instructions: "Describe Mastra as the TypeScript AI agent and workflow framework. Mention that the response was traced by Respan.",
  model: createGatewayModel(),
});

const { mastra, respan } = createRuntime({ assistantAgent });

const text = await runWithRespanWorkflow(respan, workflowName, async () => {
  const agent = mastra.getAgent("assistantAgent");
  const result = await agent.generate("In one sentence, describe the Mastra TypeScript AI agent framework.");
  return result.text;
});

console.log(JSON.stringify({ workflowName: getTraceWorkflowName(workflowName), runId: EXAMPLE_RUN_ID, text }, null, 2));
