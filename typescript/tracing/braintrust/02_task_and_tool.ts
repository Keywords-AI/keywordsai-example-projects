import {
  createRuntime,
  logExampleResult,
  rowId,
  runWithBraintrustWorkflow,
  secondsAgo,
} from "./_shared.js";

const workflowName = "Braintrust TypeScript Task Tool";
const { respan, instrumentor } = createRuntime();

function lookupCityNotes(city: string): { city: string; notes: string[] } {
  return {
    city,
    notes: [
      "Use compact bullet points.",
      "Mention one landmark and one food detail.",
    ],
  };
}

const result = await runWithBraintrustWorkflow(respan, workflowName, async () => {
  const taskSpanId = rowId("city-brief-task-span");
  const rootSpanId = rowId("city-brief-root");
  const toolOutput = lookupCityNotes("Kyoto");
  const brief = "Kyoto: Fushimi Inari is iconic; yudofu is a calm local food pick.";

  instrumentor.exportRecord({
    id: rowId("city-brief-task"),
    project_id: "respan-example",
    log_id: "g",
    span_id: taskSpanId,
    root_span_id: rootSpanId,
    created: new Date().toISOString(),
    span_attributes: {
      type: "task",
      name: "braintrust.plan_city_brief",
    },
    input: { city: "Kyoto", format: "one sentence" },
    output: { brief },
    metrics: { start: secondsAgo(3), end: secondsAgo(1) },
    metadata: { feature: "task" },
    tags: ["braintrust", "task"],
  });

  instrumentor.exportRecord({
    id: rowId("city-notes-tool"),
    project_id: "respan-example",
    log_id: "g",
    span_id: rowId("city-notes-tool-span"),
    root_span_id: rootSpanId,
    span_parents: [taskSpanId],
    created: new Date().toISOString(),
    span_attributes: {
      type: "tool",
      name: "lookup_city_notes",
    },
    input: { name: "lookup_city_notes", arguments: { city: "Kyoto" } },
    output: toolOutput,
    metrics: { start: secondsAgo(2), end: secondsAgo(1.5) },
    metadata: { feature: "tool" },
    scores: { useful: 1 },
    tags: ["braintrust", "tool"],
  });

  return { brief, toolOutput };
});

logExampleResult(workflowName, result);
