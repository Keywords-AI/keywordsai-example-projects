import {
  createOpenAIClient,
  createRuntime,
  EXAMPLE_MODEL,
  logExampleResult,
  rowId,
  runWithBraintrustWorkflow,
  secondsAgo,
} from "./_shared.js";

const workflowName = "Braintrust TypeScript LLM Chat";
const { respan, instrumentor } = createRuntime();
const openai = createOpenAIClient();

const text = await runWithBraintrustWorkflow(respan, workflowName, async () => {
  const messages = [
    { role: "system" as const, content: "Reply in one concise sentence." },
    { role: "user" as const, content: "Describe what Braintrust tracing records." },
  ];
  const completion = await openai.chat.completions.create({
    model: EXAMPLE_MODEL,
    messages,
  });
  const output = completion.choices[0]?.message?.content ?? "";

  instrumentor.exportRecord({
    id: rowId("llm-chat"),
    project_id: "respan-example",
    log_id: "g",
    span_id: rowId("llm-chat-span"),
    root_span_id: rowId("llm-chat-root"),
    created: new Date().toISOString(),
    span_attributes: {
      type: "llm",
      name: "braintrust.llm.chat",
      model: EXAMPLE_MODEL,
      provider: "openai",
    },
    input: { messages },
    output: { content: output },
    metrics: {
      start: secondsAgo(2),
      end: secondsAgo(1),
      prompt_tokens: completion.usage?.prompt_tokens ?? 0,
      completion_tokens: completion.usage?.completion_tokens ?? 0,
      tokens: completion.usage?.total_tokens ?? 0,
    },
    metadata: {
      feature: "llm_chat",
      finish_reason: completion.choices[0]?.finish_reason ?? "unknown",
    },
    scores: { concise: 1 },
    tags: ["braintrust", "llm", "chat"],
  });

  return output;
});

logExampleResult(workflowName, { model: EXAMPLE_MODEL, text });
