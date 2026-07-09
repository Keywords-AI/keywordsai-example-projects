import fs from "node:fs/promises";
import path from "node:path";
import {
  codexThreadOptions,
  createCodex,
  createRespan,
  createScratchWorkspace,
  logExampleResult,
  runWithCodexWorkflow,
  shutdownRespan,
  withCodexRetries,
  withTimeout,
} from "./_shared.js";

const workflowName = "codex-sdk-ts-file-change";
const respan = createRespan("codex-sdk-typescript-file-change");

try {
  const details = await runWithCodexWorkflow(respan, workflowName, async () =>
    await withCodexRetries(workflowName, async () => {
      const scratchDir = await createScratchWorkspace("file-change");
      const codex = createCodex();
      const thread = codex.startThread(
        codexThreadOptions({
          workingDirectory: scratchDir,
          sandboxMode: "workspace-write",
        }),
      );
      const result = await withTimeout(
        thread.run(
          "Create a file named codex_respan_note.txt containing exactly: Respan Codex SDK file change traced. Then reply with done.",
        ),
        workflowName,
      );
      const changedFile = path.join(scratchDir, "codex_respan_note.txt");
      const fileExists = await fs.access(changedFile).then(() => true, () => false);
      const fileContent = fileExists ? await fs.readFile(changedFile, "utf8") : "";

      return {
        finalResponse: result.finalResponse,
        fileExists,
        fileContent: fileContent.trim(),
        scratchDir,
        itemTypes: result.items.map((item) => item.type),
      };
    }),
  );

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
