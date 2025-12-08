import { createAnthropic } from "@ai-sdk/anthropic";
import { generateText, tool } from "ai";
import { z } from "zod";

const apiKey = process.env.KEYWORDSAI_API_KEY;
const baseURL = process.env.KEYWORDSAI_BASE_URL;

const anthropic = createAnthropic({
  baseURL,
  apiKey,
});
const result = await generateText({
  model: anthropic("claude-3-5-sonnet-20240620"),
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "What is the weather in San Francisco?" },
      ],
    },
  ],
  tools: {
    weather: tool({
      description: "Get the weather in a location",
      parameters: z.object({
        location: z.string().describe("The location to get the weather for"),
      }),
      execute: async ({ location }) => ({
        location,
        temperature: 72 + Math.floor(Math.random() * 21) - 10,
      }),
    }),
  },
});
debugger;
console.log(JSON.stringify(result, null, 2));
