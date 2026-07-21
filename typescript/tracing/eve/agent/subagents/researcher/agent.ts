import { defineAgent } from "eve";
import { mockModel } from "eve/evals";

export default defineAgent({
  description:
    "Return a deterministic research marker for the instrumentation example.",
  modelContextWindowTokens: 1_000_000,
  model: mockModel({
    provider: "respan-example",
    modelId: "eve-deterministic-researcher",
    respond: () => ({
      text: "RESEARCH_MARKER=eve-lineage-ok",
      usage: { inputTokens: 19, outputTokens: 6 },
    }),
  }),
});
