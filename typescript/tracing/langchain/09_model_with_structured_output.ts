import { fakeModel } from "@langchain/core/testing";
import { z } from "zod";

import { initRespan, shutdown, tracingConfig } from "./_shared";

const Movie = z.object({
  title: z.string(),
  year: z.number(),
  director: z.string(),
});

export async function modelWithStructuredOutput(): Promise<void> {
  const runtime = await initRespan("typescript-langchain-model-with-structured-output");
  const model = fakeModel().structuredResponse({
    title: "Inception",
    year: 2010,
    director: "Christopher Nolan",
  });
  const structuredModel = model.withStructuredOutput(Movie);

  try {
    const response = await structuredModel.invoke(
      "Provide details for the movie Inception.",
      tracingConfig(runtime, "model_with_structured_output"),
    );
    console.log(JSON.stringify(response));
  } finally {
    await shutdown(runtime);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await modelWithStructuredOutput();
}
