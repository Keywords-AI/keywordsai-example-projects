import {
  createAgentContext,
  createRuntime,
  emit,
  logExampleResult,
  runWithFlueTrace,
} from "./_shared.js";

const workflowName = "Flue Direct Agent Coverage.workflow";
const { respan } = createRuntime(workflowName);

const result = await runWithFlueTrace(respan, workflowName, async () => {
  const ctx = createAgentContext("support-agent", {
    message: "Summarize the account state and apply the policy skill.",
  });

  emit(ctx, { type: "agent_start" });
  ctx.log.info("agent session opened", { channel: "direct", session: "support" });
  emit(ctx, {
    type: "operation_start",
    operationId: "skill-op",
    operationKind: "skill",
  });
  emit(ctx, {
    type: "turn_start",
    operationId: "skill-op",
    turnId: "turn-skill",
    purpose: "agent",
  });
  emit(ctx, {
    type: "turn_request",
    operationId: "skill-op",
    turnId: "turn-skill",
    purpose: "agent",
    model: "anthropic/claude-haiku-4-5",
    provider: "anthropic",
    api: "messages",
    input: {
      systemPrompt: "Use the policy skill before answering.",
      messages: [
        { role: "user", content: "Can this account receive a refund?" },
      ],
      tools: [
        {
          name: "policy_lookup",
          description: "Lookup a policy by topic.",
          parameters: { type: "object", properties: { topic: { type: "string" } } },
        },
      ],
    },
    reasoning: "low",
  });
  emit(ctx, {
    type: "turn",
    operationId: "skill-op",
    turnId: "turn-skill",
    purpose: "agent",
    durationMs: 90,
    model: "anthropic/claude-haiku-4-5",
    provider: "anthropic",
    api: "messages",
    output: {
      role: "assistant",
      content: [
        { type: "thinking", thinking: "The refund policy applies." },
        { type: "text", text: "The account is eligible for a standard refund review." },
      ],
    },
    usage: {
      input: 48,
      output: 18,
      cacheRead: 0,
      cacheWrite: 2,
      totalTokens: 66,
      cost: { input: 0.00001, output: 0.00002, cacheRead: 0, cacheWrite: 0, total: 0.00003 },
    },
    isError: false,
  });
  emit(ctx, {
    type: "operation",
    operationId: "skill-op",
    operationKind: "skill",
    durationMs: 110,
    isError: false,
    result: { text: "The account is eligible for a standard refund review." },
  });
  emit(ctx, {
    type: "submission_settled",
    submissionId: "submission-policy-review",
    outcome: "completed",
  });
  emit(ctx, {
    type: "agent_end",
    messages: [
      { role: "assistant", content: "The account is eligible for a standard refund review." },
    ],
  });

  return { answer: "The account is eligible for a standard refund review." };
});

logExampleResult(workflowName, {
  expectedSpans: ["task", "chat", "task", "task", "agent"],
  result,
});
