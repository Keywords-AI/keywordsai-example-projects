import { RUN_ID, createRespan, shutdownRespan } from "./_shared.js";
import { runChatCompletion } from "./01_chat_completion.js";
import { runToolCalling } from "./02_tool_calling.js";
import { runStreaming } from "./03_streaming.js";
import { runEmbeddings } from "./04_embeddings.js";

console.log(JSON.stringify({ runId: RUN_ID, exampleSet: "typescript-openrouter" }, null, 2));
const respan = createRespan();
try {
  await runChatCompletion(respan);
  await runToolCalling(respan);
  await runStreaming(respan);
  await runEmbeddings(respan);
} finally {
  await shutdownRespan(respan);
}
