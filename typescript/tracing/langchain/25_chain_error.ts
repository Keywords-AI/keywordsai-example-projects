import { RunnableLambda } from "@langchain/core/runnables";

import { initRespan, shutdown, tracingConfig } from "./_shared";

export async function chainError(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-chain-error");
  const chain = RunnableLambda.from(() => {
    throw new Error("chain failed");
  });

  try {
    await chain.invoke("bad input", tracingConfig(runtime, "chain_error"));
  } catch (error) {
    console.log(`caught expected error: ${(error as Error).message}`);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await chainError();
}
