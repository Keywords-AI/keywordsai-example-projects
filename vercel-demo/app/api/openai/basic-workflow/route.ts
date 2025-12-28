import { createOpenAI, openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  // Destructure 'id' as well, which can be used for persisting chat history in a DB
  const { message, id } = await req.json();
  const steps = [];

  const keywordsaiApiKeyFromUI = req.headers.get('x-keywordsai-api-key')?.trim();
  if (keywordsaiApiKeyFromUI) {
    (globalThis as any).__KEYWORDSAI_RUNTIME_API_KEY__ = keywordsaiApiKeyFromUI;
  }

  console.log('chat id:', id || 'no-id-provided'); 

  // Header creator for KeywordsAI system parameters
  const createHeader = () => {
    return {
      'X-Data-Keywordsai-Params': Buffer.from(JSON.stringify({
        customer_identifier: "user_demo_123",
        trace_group_identifier: "basic_handoff_group",
        prompt_unit_price: 100000
      })).toString('base64')
    }
  }

  const apiKeyFromUI = req.headers.get('x-openai-api-key')?.trim();
  const openaiProvider = apiKeyFromUI ? createOpenAI({ apiKey: apiKeyFromUI }) : openai;

  // Step 1: Triage Agent
  const triageResult = await generateText({
    model: openaiProvider('gpt-4o-mini'),
    prompt: `Analyze the language of this message: "${message}". Return ONLY the language name.`,
    headers: createHeader(),
    experimental_telemetry: {
      isEnabled: true,
      functionId: "triage-agent",
      metadata: { 
        agent: 'Triage Agent', 
        step: 1,
        environment: 'demo'
      }
    },
  });

  const language = triageResult.text.trim();
  steps.push({
    agent: 'Triage Agent',
    action: 'Analyzing language...',
    output: `Detected Language: ${language}.`
  });

  // Step 2: Specialist Agent
  const specialistResult = await generateText({
    model: openaiProvider('gpt-4o-mini'),
    prompt: `You are a specialist in ${language}. Respond to this message in ${language}: "${message}"`,
    headers: createHeader(), // Using the same header function for consistency
    experimental_telemetry: {
      isEnabled: true,
      functionId: "specialist-agent",
      metadata: { 
        agent: `${language} Specialist`, 
        step: 2,
        custom_tag: 'pro_user'
      }
    },
  });

  steps.push({
    agent: `${language} Specialist`,
    action: `Generating ${language} response...`,
    output: specialistResult.text
  });

  return Response.json({ 
    steps, 
    system_metadata: { 
      prompt_unit_price: 100000,
      customer_id: "user_demo_123",
      group_id: "basic_handoff_group"
    },
    custom_metadata: { environment: 'demo', custom_tag: 'pro_user' }
  });
}
