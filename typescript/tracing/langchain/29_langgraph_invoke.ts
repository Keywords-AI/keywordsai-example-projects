import { END, START, StateGraph, StateSchema } from "@langchain/langgraph";
import { z } from "zod";

import { initRespan, shutdown, tracingConfig } from "./_shared";

const State = new StateSchema({
  topic: z.string(),
  joke: z.string().default(""),
});

export async function langgraphInvoke(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-langgraph-invoke");
  const graph = new StateGraph(State)
    .addNode("refineTopic", (state: typeof State.State) => ({
      topic: `${state.topic} and tracing`,
    }))
    .addNode("generateJoke", (state: typeof State.State) => ({
      joke: `A joke about ${state.topic}`,
    }))
    .addEdge(START, "refineTopic")
    .addEdge("refineTopic", "generateJoke")
    .addEdge("generateJoke", END)
    .compile();

  try {
    const result = await graph.invoke(
      { topic: "LangChain" },
      tracingConfig(runtime, "langgraph_invoke", { framework: "langgraph" }),
    );
    console.log(result.joke);
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await langgraphInvoke();
}
