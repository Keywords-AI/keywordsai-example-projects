import { createOpenAI, openai } from '@ai-sdk/openai';
import { generateText, tool } from 'ai';
import { z } from 'zod';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { message } = await req.json();
  const steps: any[] = [];

  const keywordsaiApiKeyFromUI = req.headers.get('x-keywordsai-api-key')?.trim();
  if (keywordsaiApiKeyFromUI) {
    (globalThis as any).__KEYWORDSAI_RUNTIME_API_KEY__ = keywordsaiApiKeyFromUI;
  }

  const apiKeyFromUI = req.headers.get('x-openai-api-key')?.trim();
  const openaiProvider = apiKeyFromUI ? createOpenAI({ apiKey: apiKeyFromUI }) : openai;

  const result = await generateText({
    model: openaiProvider('gpt-4o-mini'),
    prompt: message || "What's the weather in Tokyo?",
    maxSteps: 5, // Allow the AI to continue after the tool call to finalize the response
    tools: {
      getWeather: tool({
        description: 'Get the weather in a location',
        parameters: z.object({
          location: z.string().describe('The city and state, e.g. San Francisco, CA'),
        }),
        execute: async ({ location }) => {
          const data = { location, temperature: '22°C', conditions: 'Sunny' };
          steps.push({
            agent: 'Weather Tool',
            action: `Fetching weather for ${location}...`,
            output: JSON.stringify(data, null, 2)
          });
          return data;
        },
      }),
    },
    experimental_telemetry: {
      isEnabled: true,
      metadata: { workflow: 'tool-use' }
    },
  });

  steps.push({
    agent: 'Assistant',
    action: 'Finalizing response based on tool data...',
    output: result.text // Now this will contain the final summarized answer
  });

  return Response.json({ steps });
}
