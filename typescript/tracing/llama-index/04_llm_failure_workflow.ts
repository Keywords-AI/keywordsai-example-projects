import { Settings } from "llamaindex";
import { randomUUID } from "node:crypto";
import { createOpenAI, runNamedWorkflow } from "./_runtime.js";

export const WORKFLOW_NAME = "llama_index_ts_llm_failure";

async function main(): Promise<void> {
  let failureName: string | undefined;
  try {
    await runNamedWorkflow(WORKFLOW_NAME, async () => {
      Settings.callbackManager.dispatchEvent(
        "query-start",
        {
          id: randomUUID(),
          query: "Exercise the expected LlamaIndex provider failure path.",
        },
        true,
      );
      Settings.llm = createOpenAI({
        baseURL: "http://127.0.0.1:1",
        maxRetries: 0,
        timeout: 1_000,
      });
      await Settings.llm.complete({
        prompt: "Exercise the expected LlamaIndex provider failure path.",
      });
    });
  } catch (error) {
    failureName = error instanceof Error ? error.name : "Error";
  }

  if (!failureName) {
    throw new Error("The intentional LlamaIndex provider failure did not occur.");
  }

  console.log(JSON.stringify({
    workflowName: WORKFLOW_NAME,
    expectedFailure: true,
    failureName,
  }));
}

await main();
