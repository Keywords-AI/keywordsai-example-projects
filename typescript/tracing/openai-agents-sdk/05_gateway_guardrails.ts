import { Agent, type InputGuardrail, type OutputGuardrail } from "@openai/agents";
import { createRuntime, shutdownRuntime, withExampleTrace } from "./_runtime.js";

const runtime = await createRuntime("openai-agents-gateway-guardrails");

const inputGuardrail: InputGuardrail = {
  name: "input_shape_check",
  runInParallel: false,
  execute: async ({ input }) => {
    const serializedInput = typeof input === "string" ? input : JSON.stringify(input);
    return {
      tripwireTriggered: false,
      outputInfo: {
        length: serializedInput.length,
        containsRunId: serializedInput.includes(runtime.runId),
      },
    };
  },
};

const outputGuardrail: OutputGuardrail = {
  name: "concise_output_check",
  execute: async ({ agentOutput }) => {
    const output = String(agentOutput);
    return {
      tripwireTriggered: false,
      outputInfo: {
        length: output.length,
        sentenceCount: output.split(".").filter(Boolean).length,
      },
    };
  },
};

try {
  const agent = new Agent({
    name: "gateway_guardrail_agent",
    instructions: "Answer in one concise sentence.",
    model: runtime.model,
    inputGuardrails: [inputGuardrail],
    outputGuardrails: [outputGuardrail],
  });

  const result = await withExampleTrace(
    runtime,
    "openai_agents_gateway_guardrails.workflow",
    async () =>
      await runtime.runner.run(
        agent,
        `Run ${runtime.runId}: explain why guardrail spans are useful.`,
        {
          maxTurns: 1,
        },
      ),
  );

  console.log(String(result.finalOutput ?? ""));
} finally {
  await shutdownRuntime(runtime);
}
