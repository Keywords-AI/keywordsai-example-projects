import { KeywordsAITelemetry } from "@keywordsai/tracing";
import { OpenAI } from "openai";
import * as dotenv from "dotenv";
dotenv.config({ path: ".env.local", override: true });

// Declare global type
declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

export function register() {
  global.keywordsai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: process.env.KEYWORDSAI_BASE_URL || "",
    logLevel: "debug",
    disableBatch: true,
    instrumentModules: {
      openAI: OpenAI,
    },
    disabledInstrumentations: ["fetch"],
  });
  global.keywordsai.initialize();
}

// Export for use in other modules - will be undefined until register() is called
export const keywordsai = global.keywordsai;
