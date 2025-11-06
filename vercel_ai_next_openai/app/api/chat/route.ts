import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  // Extract the `messages` from the body of the request
  const { messages, id } = await req.json();

  console.log('chat id', id); // can be used for persisting the chat
  const createHeader = () => {
    return {
      'X-Data-Keywordsai-Params': Buffer.from(JSON.stringify({
        prompt_unit_price: 100000
      })).toString('base64')
    }
  }

  // Call the language model
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    async onFinish({ text, toolCalls, toolResults, usage, finishReason }) {
      // implement your own logic here, e.g. for storing messages
      // or recording token usage
    },
    experimental_telemetry: {
      isEnabled: true,
      metadata: {
        customer_identifier: "customer_from_metadata",
        prompt_unit_price: 100000
      },
      headers: createHeader()
    }
  });

  // Respond with the stream
  return result.toDataStreamResponse();
}
