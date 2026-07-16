import { Agent, handoff } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-handoff");

try {
  const refundAgent = new Agent({
    name: "refund_specialist",
    handoffDescription: "Handles refund eligibility questions.",
    instructions:
      "You are the refund specialist. Answer in one concise sentence and mention that this was routed by handoff.",
    model: runtime.model,
  });

  const triageAgent = new Agent({
    name: "support_triage_agent",
    instructions:
      "If the user asks about refunds, immediately call transfer_to_refund_specialist. Do not answer refund questions yourself.",
    model: runtime.model,
    handoffs: [
      handoff(refundAgent, {
        toolNameOverride: "transfer_to_refund_specialist",
        toolDescriptionOverride: "Transfer refund questions to the refund specialist.",
        onHandoff: () => {
          console.log("handoff: refund_specialist");
        },
      }),
    ],
  });

  const result = await withExampleTrace(
    runtime,
    "openai_agents_gateway_handoff.workflow",
    async () =>
      await runtime.runner.run(
        triageAgent,
        `Run ${runtime.runId}: I need help understanding whether a refund is available.`,
        {
          maxTurns: 4,
        },
      ),
  );

  console.log(String(result.finalOutput ?? ""));
} finally {
  await shutdownRuntime(runtime);
}
