import { llm, voice } from "@livekit/agents";
import {
  closeSession,
  createRespan,
  ExampleFakeLLM,
  logExampleResult,
  runWithExampleTrace,
  summarizeRunEvents,
} from "./_shared.js";

const workflowName = "TypeScript LiveKit Agent Handoff Example";

export async function agentHandoffExample(): Promise<void> {
  const respan = createRespan("typescript-livekit-agent-handoff-example");
  await respan.initialize();

  try {
    const events = await runWithExampleTrace(respan, workflowName, async () => {
      const billingAgent = new voice.Agent({
        id: "billing_specialist",
        instructions: "Handle billing questions with a concise next step.",
      });

      const session = new voice.AgentSession({
        llm: new ExampleFakeLLM([
          {
            input: "Please route me to billing.",
            toolCalls: [{ name: "handoff_to_billing", args: {} }],
          },
        ]),
      });

      const triageAgent = new voice.Agent({
        id: "triage_agent",
        instructions: "Route billing requests to the billing specialist.",
        tools: {
          handoff_to_billing: llm.tool({
            description: "Transfer the session to the billing specialist.",
            execute: async () => llm.handoff({
              agent: billingAgent,
              returns: "Transferred to billing specialist.",
            }),
          }),
        },
      });

      try {
        await session.start({ agent: triageAgent, record: false });
        const result = await session.run({ userInput: "Please route me to billing." }).wait();
        return summarizeRunEvents(result);
      } finally {
        await closeSession(session);
      }
    });

    logExampleResult(workflowName, {
      events,
    });
  } finally {
    await respan.shutdown();
  }
}

await agentHandoffExample();
