/**
 * Create Prompt Example
 * Documentation: https://docs.keywordsai.co/get-started/quickstart/create-a-prompt
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;
const DEFAULT_MODEL = process.env.DEFAULT_MODEL || "gpt-4o";

interface Message {
  role: string;
  content: string;
}

interface PromptResponse {
  id?: string;
  prompt_id?: string;
  name?: string;
  [key: string]: unknown;
}

interface PromptVersionResponse {
  version_number?: number;
  version?: number;
  [key: string]: unknown;
}

interface CreatePromptVersionOptions {
  promptId: string;
  messages: Message[];
  description?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  variables?: Record<string, unknown>;
}

export async function createPrompt(name: string, description: string = ""): Promise<PromptResponse> {
  const url = `${BASE_URL}/prompts/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify({ name, description }),
  });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: PromptResponse = await response.json();
  console.log(`[OK] Prompt created: ${data.prompt_id || data.id}`);
  return data;
}

export async function createPromptVersion(options: CreatePromptVersionOptions): Promise<PromptVersionResponse> {
  const { promptId, messages, description, model, temperature, maxTokens, variables } = options;

  const url = `${BASE_URL}/prompts/${promptId}/versions/`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = { messages };
  if (description) payload.description = description;
  if (model) payload.model = model;
  if (temperature !== undefined) payload.temperature = temperature;
  if (maxTokens !== undefined) payload.max_tokens = maxTokens;
  if (variables) payload.variables = variables;

  const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data: PromptVersionResponse = await response.json();
  console.log(`[OK] Version created: ${data.version_number ?? data.version}`);
  return data;
}

export async function listPrompts(): Promise<PromptResponse[]> {
  const url = `${BASE_URL}/prompts/list`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const response = await fetch(url, { method: "GET", headers });
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

  const data = await response.json();
  const prompts: PromptResponse[] = Array.isArray(data) ? data : data.prompts || [];
  console.log(`[OK] Found ${prompts.length} prompt(s)`);
  return prompts;
}

async function main() {
  console.log("Create Prompt Example\n");

  // Create prompt
  console.log("[1] Creating prompt");
  const prompt = await createPrompt("Customer Support Assistant", "A helpful assistant for customer support");
  const promptId = prompt.prompt_id || prompt.id;

  if (promptId) {
    // Create version
    console.log("\n[2] Creating version with messages");
    await createPromptVersion({
      promptId,
      messages: [
        { role: "system", content: "You are a helpful customer support assistant." },
        { role: "user", content: "{{user_query}}" },
      ],
      description: "Initial version",
      model: DEFAULT_MODEL,
      temperature: 0.7,
      maxTokens: 256,
      variables: { user_query: "How can I help you?" },
    });

    // List prompts
    console.log("\n[3] Listing all prompts");
    await listPrompts();
  }

  console.log("\nDone.");
}

const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
