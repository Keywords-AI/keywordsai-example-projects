import OpenAI from "openai";
import { keywordsai } from "./keywordsai-init";

// Create OpenAI instance - will be automatically instrumented by KeywordsAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "",
});

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function generateChatCompletion(messages: ChatMessage[]) {
  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async (params: {
      messages: ChatMessage[];
      model: string;
      temperature: number;
    }) => {
      const completion = await openai.chat.completions.create({
        model: params.model,
        messages: params.messages,
        temperature: params.temperature,
      });

      const assistantMessage = completion.choices[0]?.message?.content;
      return {
        message: assistantMessage,
        usage: completion.usage,
        model: completion.model,
        id: completion.id,
      };
    },
    {
      messages: messages,
      model: "gpt-4o-mini",
      temperature: 0.7,
    }
  );
}

export async function generateChatCompletionStream(messages: ChatMessage[]) {
  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletionStream",
    },
    async (params: {
      messages: ChatMessage[];
      model: string;
      temperature: number;
    }) => {
      const stream = openai.chat.completions.create({
        model: params.model,
        messages: params.messages,
        temperature: params.temperature,
        stream: true,
      });

      return stream;
    },
    {
      messages: messages,
      model: "gpt-4o-mini",
      temperature: 0.7,
    }
  );
}
