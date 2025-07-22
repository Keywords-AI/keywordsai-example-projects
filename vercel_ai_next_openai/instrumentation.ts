import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-vercel";
import { KeywordsAITelemetry } from "@keywordsai/tracing";
// import * as dotenv from "dotenv";

// dotenv.config({
//   path: ".env.local",
//   override: true,
// });

export function register() {
  console.log(
    "registering instrumentation, base url",
    process.env.KEYWORDSAI_BASE_URL,
    "api key",
    process.env.KEYWORDSAI_API_KEY?.slice(0, 4) + "..."
  );
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const telemetry = new KeywordsAITelemetry({
      apiKey: process.env.KEYWORDSAI_API_KEY?.split(" ")[0],
      // baseUrl: process.env.KEYWORDSAI_BASE_URL,
      baseUrl:
        "https://webhook.site/1b14839d-88c2-4b4e-9094-16aa6d43bc4b/api/integrations/v1/traces/ingest",
      // debug: true
    });
  }
  registerOTel({
    serviceName: "next-app",
    traceExporter: new KeywordsAIExporter({
      apiKey: process.env.KEYWORDSAI_API_KEY?.split(" ")[0],
      // baseUrl: process.env.KEYWORDSAI_BASE_URL,
      baseUrl:
        "https://webhook.site/1b14839d-88c2-4b4e-9094-16aa6d43bc4b/api/integrations/v1/traces/ingest",
      debug: true,
    }),
  });
}
