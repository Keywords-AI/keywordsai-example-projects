import { getWeather, initRespan, shutdown, tracingConfig } from "./_shared";

export async function toolInvoke(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-tool-invoke");

  try {
    const result = await getWeather.invoke(
      { city: "Tokyo" },
      tracingConfig(runtime, "tool_invoke"),
    );
    console.log(result);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await toolInvoke();
}
