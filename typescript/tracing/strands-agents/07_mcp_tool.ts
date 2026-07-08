import {
  createAgent,
  createDemoMcpEnvironment,
  logExampleResult,
  resultText,
  runStrandsExample,
} from "./_shared.js";

const workflowName = "Strands Agents TS MCP Tool.workflow";
const result = await runStrandsExample({
  appName: "strands-agents-typescript-examples",
  workflowName,
  fn: async () => {
    const env = await createDemoMcpEnvironment();
    try {
      const agent = createAgent("mcp", { tools: [env.client] });
      return await agent.invoke("Use the MCP summarize_city tool for Lisbon.");
    } finally {
      await env.close();
    }
  },
});

logExampleResult(workflowName, {
  output: resultText(result),
  stopReason: result.stopReason,
});
