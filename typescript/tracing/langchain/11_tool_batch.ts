import { getWeather, initRespan, shutdown, tracingConfig } from "./_shared";

export async function toolBatch(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-tool-batch");

  try {
    const result = await getWeather.batch(
      [{ city: "Tokyo" }, { city: "Paris" }],
      tracingConfig(runtime, "tool_batch"),
    );
    console.log(result.join(" | "));
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await toolBatch();
}
