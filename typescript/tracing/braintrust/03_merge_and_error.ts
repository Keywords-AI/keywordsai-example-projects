import {
  createRuntime,
  EXAMPLE_MODEL,
  logExampleResult,
  rowId,
  runWithBraintrustWorkflow,
  secondsAgo,
} from "./_shared.js";

const workflowName = "Braintrust TypeScript Merge Error";
const { respan, instrumentor } = createRuntime();

const result = await runWithBraintrustWorkflow(respan, workflowName, async () => {
  const rootSpanId = rowId("merge-root");
  const llmSpanId = rowId("merge-llm-span");

  instrumentor.exportRecords([
    {
      id: rowId("merged-tool-call"),
      project_id: "respan-example",
      log_id: "g",
      span_id: llmSpanId,
      root_span_id: rootSpanId,
      created: new Date().toISOString(),
      span_attributes: {
        type: "llm",
        name: "braintrust.merged.tool_call",
        model: EXAMPLE_MODEL,
        provider: "openai",
        tools: [
          {
            name: "get_exchange_rate",
            description: "Return a mocked exchange-rate quote.",
            parameters: {
              type: "object",
              properties: {
                base: { type: "string" },
                quote: { type: "string" },
              },
              required: ["base", "quote"],
            },
          },
        ],
      },
      input: {
        messages: [
          { role: "user", content: "Use a tool to quote USD to JPY." },
        ],
      },
      metrics: {
        start: secondsAgo(3),
        prompt_tokens: 11,
      },
      metadata: { feature: "merge_initial" },
      tags: ["braintrust", "merge"],
    },
    {
      id: rowId("merged-tool-call"),
      project_id: "respan-example",
      log_id: "g",
      span_id: rowId("ignored-merge-span"),
      root_span_id: rowId("ignored-merge-root"),
      _is_merge: true,
      output: {
        content: "I would call get_exchange_rate for USD to JPY.",
        tool_calls: [
          {
            id: "call_exchange_rate",
            name: "get_exchange_rate",
            arguments: { base: "USD", quote: "JPY" },
          },
        ],
      },
      metrics: {
        end: secondsAgo(1),
        completion_tokens: 7,
        tokens: 18,
      },
      metadata: { feature: "merge_update" },
      tags: ["tool_call"],
    },
  ]);

  instrumentor.exportRecord({
    id: rowId("failing-postprocess"),
    project_id: "respan-example",
    log_id: "g",
    span_id: rowId("failing-postprocess-span"),
    root_span_id: rootSpanId,
    span_parents: [llmSpanId],
    created: new Date().toISOString(),
    span_attributes: {
      type: "task",
      name: "braintrust.failing_postprocess",
    },
    input: { step: "postprocess", value: "tool-call-output" },
    error: { message: "intentional Braintrust example postprocess failure" },
    metrics: { start: secondsAgo(1), end: secondsAgo(0.5) },
    metadata: { feature: "error_row" },
    tags: ["braintrust", "error"],
  });

  return {
    mergedSpan: "braintrust.merged.tool_call",
    errorSpan: "braintrust.failing_postprocess",
  };
});

logExampleResult(workflowName, result);
