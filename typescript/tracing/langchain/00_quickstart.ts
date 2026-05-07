import "dotenv/config";

import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { FakeListChatModel } from "@langchain/core/utils/testing";
import { LangChainInstrumentor } from "@respan/instrumentation-langchain";
import { Respan } from "@respan/respan";

export async function langchainInstrumentationQuickstart(): Promise<void> {
  const apiKey = process.env.RESPAN_API_KEY;
  const langchain = new LangChainInstrumentor();
  let respan: Respan | undefined;

  if (apiKey) {
    respan = new Respan({
      apiKey,
      baseURL: process.env.RESPAN_BASE_URL,
      appName: "typescript-langchain-quickstart",
      instrumentations: [langchain],
      logLevel: "error",
      silenceInitializationMessage: true,
    });
    await respan.initialize();
  } else {
    console.log("RESPAN_API_KEY is not set; running locally without exporting spans.");
  }

  const model = new FakeListChatModel({
    responses: ["Hello from a traced TypeScript LangChain run."],
  });
  const config = apiKey
    ? langchain.addCallback({
        runName: "quickstart",
        tags: ["respan-langchain-example", "quickstart"],
        metadata: { example: "quickstart" },
      })
    : {
        runName: "quickstart",
        tags: ["respan-langchain-example", "quickstart"],
        metadata: { example: "quickstart" },
      };

  try {
    const response = await model.invoke(
      [
        new SystemMessage("Reply in one short sentence."),
        new HumanMessage("Say hello to Respan tracing."),
      ],
      config,
    );
    console.log(response.content);
  } finally {
    await respan?.shutdown().catch(() => undefined);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await langchainInstrumentationQuickstart();
}
