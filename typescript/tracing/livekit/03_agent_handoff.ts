import { llm, voice } from "@livekit/agents";
import {
  closeSession,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
  summarizeRunEvents,
} from "./_shared.js";

const workflowName = "TypeScript LiveKit Agent Handoff Example";

export async function agentHandoffExample(): Promise<void> {
  const respan = createRespan("typescript-livekit-agent-handoff-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const billingAgent = new voice.Agent({
        id: "billing_specialist",
        instructions: "Handle billing questions with a concise next step.",
      });

      const session = new voice.AgentSession({
        llm: new voice.testing.FakeLLM([
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
        return await session.run({ userInput: "Please route me to billing." }).wait();
      } finally {
        await closeSession(session);
      }
    });

    logExampleResult(workflowName, {
      events: summarizeRunEvents(result),
    });
  } finally {
  }
}

await agentHandoffExample();
