import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-vercel";

console.log("registering instrumentation, base url", process.env.KEYWORDSAI_BASE_URL);
export function register() {
  registerOTel({
    serviceName: "next-app",
    traceExporter: new KeywordsAIExporter({
      apiKey: process.env.KEYWORDSAI_API_KEY,
      baseUrl: process.env.KEYWORDSAI_BASE_URL,
      debug: true
    }),
  });
}
