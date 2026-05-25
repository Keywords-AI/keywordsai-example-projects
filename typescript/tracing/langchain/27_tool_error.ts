import { tool } from "langchain";
import { z } from "zod";

import { initRespan, shutdown, tracingConfig } from "./_shared";

const failingTool = tool(
  ({ key }: { key: string }) => {
    throw new Error(`no result for ${key}`);
  },
  {
    name: "failing_lookup",
    description: "Fail for missing keys.",
    schema: z.object({ key: z.string() }),
  },
);

export async function toolError(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-tool-error");

  try {
    await failingTool.invoke(
      { key: "missing" },
      tracingConfig(runtime, "tool_error"),
    );
  } catch (error) {
    console.log(`caught expected error: ${(error as Error).message}`);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await toolError();
}
