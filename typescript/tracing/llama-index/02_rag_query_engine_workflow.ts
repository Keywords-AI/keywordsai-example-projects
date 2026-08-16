import { Document, Settings, VectorStoreIndex } from "llamaindex";
import { DeterministicEmbedding } from "./_deterministic_embedding.js";
import { TracedMockLLM } from "./_deterministic_llm.js";
import { runNamedWorkflow } from "./_runtime.js";

export const WORKFLOW_NAME = "llama_index_ts_rag_query_engine";

async function main(): Promise<void> {
  const answer = await runNamedWorkflow(WORKFLOW_NAME, async () => {
    Settings.llm = new TracedMockLLM({
      responseMessage: "Inspect the workflow, retrieval task, and chat span in Respan.",
    });
    Settings.embedModel = new DeterministicEmbedding();

    const documents = [
      new Document({
        text: "Respan captures traces for LLM applications and shows workflow, task, tool, and chat spans.",
        metadata: { source: "respan-overview" },
      }),
      new Document({
        text: "The LlamaIndex TypeScript example set uses readable workflow names so traces can be found quickly.",
        metadata: { source: "example-guidance" },
      }),
    ];

    const index = await VectorStoreIndex.fromDocuments(documents);
    const queryEngine = index.asQueryEngine({ similarityTopK: 2 });
    return queryEngine.query({
      query: "What should I look for in Respan after running this LlamaIndex example?",
    });
  });

  console.log(`[${WORKFLOW_NAME}] ${String(answer)}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
