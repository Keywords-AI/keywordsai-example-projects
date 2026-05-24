import { OpenAIChatModel } from "beeai-framework/adapters/openai/backend/chat";
import { UserMessage } from "beeai-framework/backend/message";
import { createBeeAIRespanRuntime, runWithBeeAIWorkflow } from "./_respan.js";

export async function runBasicChat(): Promise<void> {
  const workflowName = "beeai_basic_chat.workflow";
  const { env, respan } = await createBeeAIRespanRuntime();

  try {
    const llm = new OpenAIChatModel(
      env.model,
      {},
      { apiKey: env.gatewayApiKey, baseURL: env.openAIEndpoint },
    );

    const prompt = "Reply with one short sentence explaining why traces help agent debugging.";
    const answer = await runWithBeeAIWorkflow(
      respan,
      workflowName,
      { prompt },
      async () => {
        const response = await llm.create({
          messages: [new UserMessage(prompt)],
        });
        return response.getTextContent();
      },
    );

    console.log(`Workflow: ${workflowName}`);
    console.log(`Model: ${env.model}`);
    console.log(`Answer: ${answer}`);
  } finally {
    await respan.flush();
  }
}

await runBasicChat();
