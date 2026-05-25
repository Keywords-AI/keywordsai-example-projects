import { Settings } from "llamaindex";
import { createOpenAI, runNamedWorkflow } from "./_runtime.js";

export const WORKFLOW_NAME = "llama_index_ts_basic_llm";

async function main(): Promise<void> {
  const response = await runNamedWorkflow(WORKFLOW_NAME, async () => {
    Settings.llm = createOpenAI();
    return Settings.llm.complete({
      prompt: "Say hello in English, Spanish, and Japanese. Keep it short.",
    });
  });

  console.log(`[${WORKFLOW_NAME}] ${response.text}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
