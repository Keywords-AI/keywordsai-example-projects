import { RunnableLambda } from "@langchain/core/runnables";

import { initRespan, shutdown, tracingConfig } from "./_shared";

export async function runnableAssignPick(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-runnable-assign-pick");
  const base = RunnableLambda.from((topic: string) => ({
    topic,
    summary: `Tracing callbacks for ${topic}`,
  }));
  const chain = base
    .assign({
      summaryLength: RunnableLambda.from(
        (input: { summary: string }) => input.summary.length,
      ),
    })
    .pick(["topic", "summaryLength"]);

  try {
    const result = await chain.invoke(
      "LangChain",
      tracingConfig(runtime, "runnable_assign_pick"),
    );
    console.log(JSON.stringify(result));
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await runnableAssignPick();
}
