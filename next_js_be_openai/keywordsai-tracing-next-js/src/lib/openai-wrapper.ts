import OpenAI from "openai";
import { KeywordsAITelemetry } from "@keywordsai/tracing";

// Declare global type
declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "",
});

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function generateChatCompletion(messages: ChatMessage[]) {
  // Access keywordsai from global object after instrumentation is initialized
  const keywordsai = global.keywordsai;
  
  if (!keywordsai) {
    throw new Error("KeywordsAI not initialized. Make sure instrumentation is set up correctly.");
  }

  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async () => {
      try {
        const completion = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: messages,
          temperature: 0.7,
        });

        const assistantMessage = completion.choices[0]?.message?.content;
        return {
          message: assistantMessage,
          usage: completion.usage,
          model: completion.model,
          id: completion.id,
        };
      } catch (error) {
        console.error("OpenAI API error:", error);
        throw error;
      }
    }
  );
}
