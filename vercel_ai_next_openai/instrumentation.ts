import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-vercel";
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
  registerOTel({
    serviceName: "next-app",
    traceExporter: new KeywordsAIExporter({
      apiKey: process.env.KEYWORDSAI_API_KEY?.split(" ")[0],
      baseUrl: process.env.KEYWORDSAI_BASE_URL,
      debug: true,
    }),
  });
}
