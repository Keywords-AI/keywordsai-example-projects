import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-vercel";

export function register() {
  const envApiKey = process.env.KEYWORDSAI_API_KEY;
  if (!envApiKey) {
    console.warn(
      "KEYWORDSAI_API_KEY not set; KeywordsAI tracing will be disabled unless a key is provided at request-time. (Recommended: run locally with env vars.)",
    );
  }

  console.log("Initializing Keywords AI Tracing...");

  // We register an exporter even if KEYWORDSAI_API_KEY is missing so a request-time key
  // (forwarded from the UI) can enable tracing without adding separate endpoints.
  const traceExporter = {
    export(spans: any[], resultCallback: (result: any) => void) {
      const apiKey =
        process.env.KEYWORDSAI_API_KEY ||
        (globalThis as any).__KEYWORDSAI_RUNTIME_API_KEY__;

      if (!apiKey) {
        // tracing disabled
        resultCallback({ code: 0 });
        return;
      }

      const exporter = new KeywordsAIExporter({
        apiKey,
        baseUrl: process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
        debug: true,
      }) as any;

      Promise.resolve(exporter.export(spans, resultCallback)).catch((err) => {
        resultCallback({
          code: 1,
          error: err instanceof Error ? err : new Error(String(err)),
        });
      });
    },
    shutdown() {
      return Promise.resolve();
    },
  } as any;

  registerOTel({
    serviceName: "next-app",
    traceExporter,
  });
}
