import { RunnableLambda } from "@langchain/core/runnables";

import { initRespan, shutdown, tracingConfig } from "./_shared";

export async function runnableWithRetry(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-runnable-with-retry");
  let attempts = 0;
  const flaky = RunnableLambda.from((input: string) => {
    attempts += 1;
    if (attempts === 1) {
      throw new Error("transient failure");
    }
    return `recovered ${input}`;
  }).withRetry({ stopAfterAttempt: 2 });

  try {
    const result = await flaky.invoke(
      "after retry",
      tracingConfig(runtime, "runnable_with_retry"),
    );
    console.log(result);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await runnableWithRetry();
}
