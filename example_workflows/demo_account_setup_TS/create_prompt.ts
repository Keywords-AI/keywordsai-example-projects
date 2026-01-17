/**
 * Create Prompt Example
 *
 * This example demonstrates how to create and manage prompts in KeywordsAI.
 * Prompts are reusable templates for LLM conversations that can be versioned and deployed.
 *
 * Documentation: https://docs.keywordsai.co/get-started/quickstart/create-a-prompt
 */

import "dotenv/config";

const BASE_URL = process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co/api";
const API_KEY = process.env.KEYWORDSAI_API_KEY;

// Prompt configuration from environment variables
const DEFAULT_MODEL = process.env.DEFAULT_MODEL || "gpt-4o";
const DEFAULT_TEMPERATURE = parseFloat(process.env.PROMPT_TEMPERATURE || "0.7");
const DEFAULT_MAX_TOKENS = parseInt(process.env.PROMPT_MAX_TOKENS || "256");

interface Message {
  role: string;
  content: string;
}

interface PromptResponse {
  id?: string;
  prompt_id?: string;
  name?: string;
  description?: string;
  [key: string]: unknown;
}

interface PromptVersionResponse {
  version_number?: number;
  version?: number;
  prompt_version_id?: string;
  messages?: Message[];
  [key: string]: unknown;
}

interface CreatePromptVersionOptions {
  promptId: string;
  messages: Message[];
  description?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  variables?: Record<string, unknown>;
  [key: string]: unknown;
}

/**
 * Create a new prompt in Keywords AI.
 */
export async function createPrompt(name: string, description: string = ""): Promise<PromptResponse> {
  const url = `${BASE_URL}/prompts/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload = {
    name,
    description,
  };

  console.log("Creating prompt...");
  console.log(`  URL: ${url}`);
  console.log(`  Name: ${name}`);
  if (description) {
    console.log(`  Description: ${description}`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: PromptResponse = await response.json();
  console.log(`\n[OK] Prompt created successfully`);
  if (data.prompt_id) {
    console.log(`  Prompt ID: ${data.prompt_id}`);
  }
  if (data.id) {
    console.log(`  Prompt ID: ${data.id}`);
  }

  return data;
}

/**
 * Create a new version of a prompt.
 */
export async function createPromptVersion(options: CreatePromptVersionOptions): Promise<PromptVersionResponse> {
  const {
    promptId,
    messages,
    description,
    model,
    temperature,
    maxTokens,
    stream,
    variables,
    ...kwargs
  } = options;

  const url = `${BASE_URL}/prompts/${promptId}/versions/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  const payload: Record<string, unknown> = {
    messages,
  };

  if (description) {
    payload.description = description;
  }
  if (model) {
    payload.model = model;
  }
  if (temperature !== undefined) {
    payload.temperature = temperature;
  }
  if (maxTokens !== undefined) {
    payload.max_tokens = maxTokens;
  }
  if (stream !== undefined) {
    payload.stream = stream;
  }
  if (variables) {
    payload.variables = variables;
  }

  Object.assign(payload, kwargs);

  console.log("Creating prompt version...");
  console.log(`  URL: ${url}`);
  console.log(`  Prompt ID: ${promptId}`);
  console.log(`  Messages: ${messages.length}`);
  if (model) {
    console.log(`  Model: ${model}`);
  }
  if (description) {
    console.log(`  Description: ${description}`);
  }
  console.log(`  Request Body: ${JSON.stringify(payload, null, 2)}`);

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: PromptVersionResponse = await response.json();
  console.log(`\n[OK] Prompt version created successfully`);
  if (data.version_number !== undefined) {
    console.log(`  Version Number: ${data.version_number}`);
  }
  if (data.prompt_version_id) {
    console.log(`  Prompt Version ID: ${data.prompt_version_id}`);
  }

  return data;
}

/**
 * List all prompts in the account.
 */
export async function listPrompts(): Promise<PromptResponse[]> {
  const url = `${BASE_URL}/prompts/list`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Listing prompts...");
  console.log(`  URL: ${url}`);

  const response = await fetch(url, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  const prompts: PromptResponse[] = Array.isArray(data) ? data : data.prompts || [];

  console.log(`\n[OK] Found ${prompts.length} prompt(s)`);
  prompts.forEach((prompt, i) => {
    console.log(`  ${i + 1}. ${prompt.name || "Unnamed"} (ID: ${prompt.prompt_id || prompt.id || "N/A"})`);
  });

  return prompts;
}

/**
 * Get a specific prompt by ID.
 */
export async function getPrompt(promptId: string): Promise<PromptResponse> {
  const url = `${BASE_URL}/prompts/${promptId}/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Getting prompt...");
  console.log(`  URL: ${url}`);
  console.log(`  Prompt ID: ${promptId}`);

  const response = await fetch(url, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: PromptResponse = await response.json();
  console.log(`\n[OK] Prompt retrieved successfully`);
  console.log(`  Name: ${data.name || "N/A"}`);
  console.log(`  Description: ${data.description || "N/A"}`);

  return data;
}

/**
 * List all versions of a prompt.
 */
export async function listPromptVersions(promptId: string): Promise<PromptVersionResponse[]> {
  const url = `${BASE_URL}/prompts/${promptId}/versions/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Listing prompt versions...");
  console.log(`  URL: ${url}`);
  console.log(`  Prompt ID: ${promptId}`);

  const response = await fetch(url, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  const versions: PromptVersionResponse[] = Array.isArray(data) ? data : data.versions || [];

  console.log(`\n[OK] Found ${versions.length} version(s)`);
  versions.forEach((version, i) => {
    const versionNum = version.version_number ?? version.version ?? "N/A";
    console.log(`  ${i + 1}. Version ${versionNum}`);
  });

  return versions;
}

/**
 * Get a specific version of a prompt.
 */
export async function getPromptVersion(promptId: string, versionNumber: number): Promise<PromptVersionResponse> {
  const url = `${BASE_URL}/prompts/${promptId}/versions/${versionNumber}/`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`,
  };

  console.log("Getting prompt version...");
  console.log(`  URL: ${url}`);
  console.log(`  Prompt ID: ${promptId}`);
  console.log(`  Version Number: ${versionNumber}`);

  const response = await fetch(url, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: PromptVersionResponse = await response.json();
  console.log(`\n[OK] Prompt version retrieved successfully`);
  if (data.messages) {
    console.log(`  Messages: ${data.messages.length}`);
  }

  return data;
}

async function main() {
  console.log("=".repeat(80));
  console.log("KeywordsAI Create Prompt Example");
  console.log("=".repeat(80));

  // Example 1: Create a simple prompt
  console.log("\n[Example 1] Creating a simple prompt");
  console.log("-".repeat(80));

  const prompt1 = await createPrompt("Customer Support Assistant", "A helpful assistant for customer support queries");
  const prompt1Id = prompt1.prompt_id || prompt1.id;

  // Example 2: Create a prompt version with messages
  console.log("\n[Example 2] Creating a prompt version with messages");
  console.log("-".repeat(80));

  let version1: PromptVersionResponse | undefined;
  if (prompt1Id) {
    version1 = await createPromptVersion({
      promptId: prompt1Id,
      messages: [
        {
          role: "system",
          content:
            "You are a helpful customer support assistant. Be polite, professional, and solution-oriented.",
        },
        {
          role: "user",
          content: "{{user_query}}",
        },
      ],
      description: "Initial version with basic customer support setup",
      model: DEFAULT_MODEL,
      temperature: DEFAULT_TEMPERATURE,
      maxTokens: DEFAULT_MAX_TOKENS,
      variables: {
        user_query: "How can I help you today?",
      },
    });
  }

  // Example 3: Create a more complex prompt with multiple messages
  console.log("\n[Example 3] Creating a complex prompt with multiple messages");
  console.log("-".repeat(80));

  const prompt2 = await createPrompt(
    "Travel Planning Assistant",
    "An AI assistant that helps users plan their travel itineraries"
  );
  const prompt2Id = prompt2.prompt_id || prompt2.id;

  let version2: PromptVersionResponse | undefined;
  if (prompt2Id) {
    version2 = await createPromptVersion({
      promptId: prompt2Id,
      messages: [
        {
          role: "system",
          content:
            "You are an expert travel planner. Help users create detailed travel itineraries based on their preferences, budget, and destination.",
        },
        {
          role: "user",
          content:
            "I want to plan a trip to {{destination}} for {{duration}} days. My budget is {{budget}} and I'm interested in {{interests}}.",
        },
      ],
      description: "Travel planning prompt with template variables",
      model: DEFAULT_MODEL,
      temperature: 0.8,
      maxTokens: 512,
      variables: {
        destination: "Paris",
        duration: "5",
        budget: "$2000",
        interests: "museums, food, architecture",
      },
    });
  }

  // Example 4: List all prompts
  console.log("\n[Example 4] Listing all prompts");
  console.log("-".repeat(80));

  const allPrompts = await listPrompts();

  // Example 5: Get a specific prompt
  console.log("\n[Example 5] Getting a specific prompt");
  console.log("-".repeat(80));

  if (prompt1Id) {
    await getPrompt(prompt1Id);
  }

  // Example 6: List prompt versions
  console.log("\n[Example 6] Listing prompt versions");
  console.log("-".repeat(80));

  if (prompt1Id) {
    const versions = await listPromptVersions(prompt1Id);

    // Example 7: Get a specific prompt version
    if (versions.length > 0) {
      console.log("\n[Example 7] Getting a specific prompt version");
      console.log("-".repeat(80));
      const versionNum = versions[0].version_number ?? versions[0].version ?? 1;
      if (typeof versionNum === "number") {
        await getPromptVersion(prompt1Id, versionNum);
      }
    }
  }

  console.log("\n" + "=".repeat(80));
  console.log("All examples completed successfully!");
  console.log("=".repeat(80));
  console.log("\nTip: You can now use these prompts in your experiments and evaluations.");
  console.log("   Visit the KeywordsAI platform to see your prompts in the Prompt Management section.");

  return {
    prompt_1: prompt1,
    prompt_2: prompt2,
    all_prompts: allPrompts,
  };
}

// Run main only if this is the entry point (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  main().catch(console.error);
}
