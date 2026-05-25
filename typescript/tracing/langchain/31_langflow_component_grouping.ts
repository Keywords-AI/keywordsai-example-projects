import { RunnableLambda } from "@langchain/core/runnables";
import { addRespanCallback, getCallbackHandler } from "@respan/instrumentation-langchain";

import { getWeather, initRespan, shutdown, type ExampleRuntime } from "./_shared";

function langflowConfig(runtime: ExampleRuntime, name: string) {
  const config = {
    runName: name,
    tags: ["respan-langchain-example", "langflow", name],
    metadata: {
      example: name,
      framework: "langflow",
      langflow_component: "RoutingComponent",
    },
  };
  if (!runtime.enabled) return config;
  return addRespanCallback(config, getCallbackHandler());
}

export async function langflowComponentGrouping(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-langflow-component-grouping");
  const routeDepartment = RunnableLambda.from((input: { department: string }) =>
    `${input.department}-workspace`,
  );

  try {
    const route = await routeDepartment.invoke(
      { department: "security" },
      langflowConfig(runtime, "langflow_route_department"),
    );
    const weather = await getWeather.invoke(
      { city: "Dublin" },
      langflowConfig(runtime, "langflow_get_weather"),
    );
    console.log(`${route}: ${weather}`);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await langflowComponentGrouping();
}
