import { KeywordsAITelemetry } from "@keywordsai/tracing";

// Declare global type
declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

export function register() {
  
  global.keywordsai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: "https://webhook.site/c40e1756-837a-4829-8994-861b8b485199",
    logLevel: "debug",
    disableBatch: true,
  });
  global.keywordsai.initialize();
}

// Export for use in other modules - will be undefined until register() is called
export const keywordsai = global.keywordsai;
