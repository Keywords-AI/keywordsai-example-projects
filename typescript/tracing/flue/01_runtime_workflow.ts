import {
  createRuntime,
  createWorkflowContext,
  emit,
  getTraceWorkflowName,
  logExampleResult,
  runWithFlueTrace,
} from "./_shared.js";

const workflowName = "Flue Runtime Feature Coverage.workflow";
const { respan } = createRuntime(workflowName);

const result = await runWithFlueTrace(respan, workflowName, async () => {
  const traceWorkflowName = getTraceWorkflowName(workflowName);
  const ctx = createWorkflowContext(traceWorkflowName, {
    city: "Paris",
    request: "Build a concise weather and travel brief.",
  });

  emit(ctx, {
    type: "run_start",
    workflowName: traceWorkflowName,
    startedAt: new Date().toISOString(),
    payload: ctx.payload,
  });
  ctx.log.info("workflow accepted request", {
    city: "Paris",
    feature: "runtime-workflow",
  });
  emit(ctx, {
    type: "operation_start",
    operationId: "prompt-op",
    operationKind: "prompt",
  });
  emit(ctx, {
    type: "turn_start",
    operationId: "prompt-op",
    turnId: "turn-weather",
    purpose: "agent",
  });
  emit(ctx, {
    type: "turn_request",
    operationId: "prompt-op",
    turnId: "turn-weather",
    purpose: "agent",
    model: "openai/gpt-4.1-nano",
    provider: "openai",
    api: "responses",
    input: {
      systemPrompt: "Answer as a compact travel planning agent.",
      messages: [
        { role: "user", content: "Plan one sunny afternoon in Paris." },
      ],
      tools: [
        {
          name: "lookup_weather",
          description: "Return deterministic weather for a city.",
          parameters: { type: "object", properties: { city: { type: "string" } } },
        },
      ],
    },
  });
  emit(ctx, {
    type: "tool_start",
    operationId: "prompt-op",
    turnId: "turn-weather",
    toolCallId: "tool-weather",
    toolName: "lookup_weather",
    args: { city: "Paris" },
  });
  emit(ctx, {
    type: "tool",
    operationId: "prompt-op",
    turnId: "turn-weather",
    toolCallId: "tool-weather",
    toolName: "lookup_weather",
    isError: false,
    result: { forecast: "sunny", temperatureC: 24 },
    durationMs: 25,
  });
  emit(ctx, {
    type: "task_start",
    operationId: "prompt-op",
    taskId: "task-reviewer",
    prompt: "Review the plan for feasibility.",
    agent: "reviewer",
    cwd: "/workspace",
  });
  emit(ctx, {
    type: "task",
    operationId: "prompt-op",
    taskId: "task-reviewer",
    agent: "reviewer",
    isError: false,
    result: { verdict: "feasible" },
    durationMs: 33,
  });
  emit(ctx, {
    type: "turn",
    operationId: "prompt-op",
    turnId: "turn-weather",
    purpose: "agent",
    durationMs: 120,
    model: "openai/gpt-4.1-nano",
    provider: "openai",
    api: "responses",
    output: {
      role: "assistant",
      content: [
        { type: "text", text: "Visit the river walk, then a museum terrace." },
        { type: "toolCall", id: "tool-weather", name: "lookup_weather", arguments: { city: "Paris" } },
      ],
    },
    usage: {
      input: 64,
      output: 22,
      cacheRead: 4,
      cacheWrite: 0,
      totalTokens: 86,
      cost: { input: 0.00001, output: 0.00002, cacheRead: 0, cacheWrite: 0, total: 0.00003 },
    },
    stopReason: "stop",
    isError: false,
  });
  emit(ctx, {
    type: "operation",
    operationId: "prompt-op",
    operationKind: "prompt",
    durationMs: 175,
    isError: false,
    result: { text: "Visit the river walk, then a museum terrace." },
    usage: {
      input: 64,
      output: 22,
      cacheRead: 4,
      cacheWrite: 0,
      totalTokens: 86,
      cost: { input: 0.00001, output: 0.00002, cacheRead: 0, cacheWrite: 0, total: 0.00003 },
    },
  });
  emit(ctx, {
    type: "compaction_start",
    operationId: "compact-op",
    reason: "manual",
    estimatedTokens: 1400,
  });
  emit(ctx, {
    type: "compaction",
    operationId: "compact-op",
    messagesBefore: 12,
    messagesAfter: 4,
    durationMs: 42,
    isError: false,
    usage: {
      input: 30,
      output: 9,
      cacheRead: 0,
      cacheWrite: 0,
      totalTokens: 39,
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
    },
  });
  emit(ctx, {
    type: "run_end",
    result: { itinerary: "river walk and museum terrace", reviewed: true },
    isError: false,
    durationMs: 260,
  });

  return { itinerary: "river walk and museum terrace", reviewed: true };
});

logExampleResult(workflowName, {
  expectedSpans: ["workflow", "task", "chat", "tool", "task", "task", "task"],
  result,
});
