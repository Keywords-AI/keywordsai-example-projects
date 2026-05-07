import { dispatchCustomEvent } from "@langchain/core/callbacks/dispatch";
import { RunnableLambda } from "@langchain/core/runnables";

import { initRespan, shutdown, tracingConfig } from "./_shared";

export async function customEvent(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-custom-event");
  const runnable = RunnableLambda.from(async (input: string) => {
    await dispatchCustomEvent("progress_event", {
      step: "halfway",
      input,
    });
    return `finished ${input}`;
  });

  try {
    const events = runnable.streamEvents("custom event example", {
      ...tracingConfig(runtime, "custom_event"),
      version: "v2",
    });
    const eventNames: string[] = [];
    for await (const event of events) {
      eventNames.push(event.event);
    }
    console.log(eventNames.join(" -> "));
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await customEvent();
}
