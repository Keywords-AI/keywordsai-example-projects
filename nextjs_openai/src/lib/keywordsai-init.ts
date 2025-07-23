import { KeywordsAITelemetry } from "@keywordsai/tracing";
import OpenAI from "openai";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config({ path: ".env.local", override: true });

// Initialize KeywordsAI telemetry singleton
const keywordsai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY || "",
  baseURL: process.env.KEYWORDSAI_BASE_URL || "",
  logLevel: "debug",
  instrumentModules: {
    openAI: OpenAI, // This enables OpenAI tracing
  },
  disableBatch: true,
});

// Initialize the telemetry singleton
keywordsai.initialize();

export { keywordsai }; 