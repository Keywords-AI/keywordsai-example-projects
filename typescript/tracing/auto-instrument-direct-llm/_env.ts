import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";

export interface AutoInstrumentExampleEnv {
  respanApiKey: string;
  respanBaseURL: string | undefined;
  gatewayApiKey: string;
  gatewayBaseURL: string;
  model: string;
  anthropicModel: string;
  azureGatewayModel: string;
  openRouterGatewayModel: string;
  vertexGatewayModel?: string;
  vertexAI?: {
    project: string;
    location: string;
    model: string;
  };
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function findRootEnv(): string {
  let current = dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 8; i += 1) {
    const candidate = join(current, ".env");
    if (existsSync(candidate)) return candidate;
    current = dirname(current);
  }
  throw new Error("Could not find respan-example-projects/.env from this example directory.");
}

function requireEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Set ${name} in respan-example-projects/.env to run this example.`);
  }
  return value;
}

function optionalEnv(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

function optionalVertexAI(): AutoInstrumentExampleEnv["vertexAI"] {
  const project = optionalEnv("GOOGLE_CLOUD_PROJECT") ?? optionalEnv("VERTEXAI_PROJECT");
  const location = optionalEnv("GOOGLE_CLOUD_LOCATION") ?? optionalEnv("VERTEXAI_LOCATION");
  if (!project || !location) return undefined;
  return {
    project,
    location,
    model: optionalEnv("VERTEXAI_MODEL") ?? "gemini-1.5-flash",
  };
}

export function loadAutoInstrumentExampleEnv(): AutoInstrumentExampleEnv {
  dotenv.config({ path: findRootEnv() });

  const respanApiKey = requireEnv("RESPAN_API_KEY");
  const gatewayApiKey = optionalEnv("RESPAN_GATEWAY_API_KEY") ?? respanApiKey;
  const gatewayBaseURL = trimTrailingSlash(
    optionalEnv("RESPAN_GATEWAY_BASE_URL") ??
      optionalEnv("RESPAN_BASE_URL") ??
      "https://api.respan.ai/api",
  );
  const model = optionalEnv("RESPAN_MODEL") ?? "gpt-4o";

  process.env.OPENAI_API_KEY = gatewayApiKey;
  process.env.OPENAI_BASE_URL = gatewayBaseURL;

  return {
    respanApiKey,
    respanBaseURL: optionalEnv("RESPAN_BASE_URL"),
    gatewayApiKey,
    gatewayBaseURL,
    model,
    anthropicModel: optionalEnv("RESPAN_ANTHROPIC_MODEL") ?? "claude-sonnet-4-5-20250929",
    azureGatewayModel: optionalEnv("RESPAN_AZURE_GATEWAY_MODEL") ?? "azure/gpt-5.5",
    openRouterGatewayModel: optionalEnv("RESPAN_OPENROUTER_GATEWAY_MODEL") ?? model,
    vertexGatewayModel: optionalEnv("RESPAN_VERTEX_GATEWAY_MODEL"),
    vertexAI: optionalVertexAI(),
  };
}
