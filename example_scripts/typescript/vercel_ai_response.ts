import { KeywordsAIExporter } from "../src/index.js";
import { BasicTracerProvider, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { trace, context } from "@opentelemetry/api";
import { AsyncHooksContextManager } from "@opentelemetry/context-async-hooks";
import { generateText, streamText } from "ai";
import { openai } from "@ai-sdk/openai"; 
import { config } from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// ============================================================================
// 1. Initialize Context Manager
// ============================================================================
const contextManager = new AsyncHooksContextManager();
contextManager.enable();
context.setGlobalContextManager(contextManager);

// ============================================================================
// 2. Configure Exporter
// ============================================================================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
config({ path: path.resolve(__dirname, "../.env") });

const exporter = new KeywordsAIExporter({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  debug: true, 
});

const provider = new BasicTracerProvider();
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

// ============================================================================
// 3. Response API Example (Strictly Aligned with API Doc)
// ============================================================================
async function main() {
  console.log("🚀 Starting Keywords AI Example (Doc Aligned)...");
  const tracer = trace.getTracer("keywords-ai-aligned-example");

  await tracer.startActiveSpan("main-execution", async (rootSpan) => {
    try {
      
      // ---------------------------------------------------------
      // Scenario 1: Standard Response
      // ---------------------------------------------------------
      console.log("\n1️⃣  Testing Standard Response...");
      
      const result = await generateText({
        // @ts-ignore
        model: openai.responses('gpt-4o'), 
        prompt: "Give me a 5-word fun fact about space.",
        
        experimental_telemetry: {
          isEnabled: true,
          // Metadata keys MUST match the API documentation fields exactly
          metadata: {
            // Corresponds to "customer_identifier" in doc
            customer_identifier: "user-new-test-999",
            
            // Corresponds to "thread_identifier" in doc
            thread_identifier: "thread-abc-123",

            // Corresponds to "log_type" in doc
            log_type: "text",

            // Corresponds to "prompt_name" in doc
            prompt_name: "test-3-response",

            // Corresponds to "customer_params" object in doc
            customer_params: {
                name: "John Doe",
                email: "user@example.com"
            }
          }
        }
      });
      console.log(`✅ Output: ${result.text}`);


      // ---------------------------------------------------------
      // Scenario 2: Streaming Response
      // ---------------------------------------------------------
      console.log("\n2️⃣  Testing Streaming Response...");
      
      const streamResult = await streamText({
        // @ts-ignore
        model: openai.responses('gpt-4o-mini'),
        prompt: "Count from 1 to 5.",
        experimental_telemetry: {
          isEnabled: true,
          metadata: {
            customer_identifier: "user-new-test-999",
            thread_identifier: "thread-abc-123",
            log_type: "text",
            prompt_name: "test-4-stream-response",
            // You can also pass customer_params here if needed
            customer_params: {
                name: "John Doe",
                email: "user@example.com"
            }
          }
        }
      });

      process.stdout.write("✅ Stream Output: ");
      for await (const chunk of streamResult.textStream) {
        process.stdout.write(chunk);
      }
      console.log("\n");


      // ---------------------------------------------------------
      // Scenario 3: Structured JSON (log_type = json)
      // ---------------------------------------------------------
      console.log("\n3️⃣  Testing JSON Response...");
      
      const jsonResult = await generateText({
        // @ts-ignore
        model: openai.responses('gpt-4o-mini'),
        prompt: "Generate a JSON with color red.",
        // @ts-ignore
        mode: 'json', 
        experimental_telemetry: {
          isEnabled: true,
          metadata: {
            customer_identifier: "user-new-test-999",
            thread_identifier: "thread-abc-123",
            prompt_name: "test-6-json-response",
            
            // Corresponds to "log_type" in doc (set to 'json' for structured output)
            log_type: "responses" 
          }
        }
      });
      console.log(`✅ JSON Output: ${jsonResult.text}`);

    } catch (error) {
      console.error("❌ Error:", error);
      rootSpan.recordException(error as Error);
    } finally {
      rootSpan.end();
    }
  });

  console.log("\n⏳ Waiting for export...");
  await new Promise((resolve) => setTimeout(resolve, 2000));
}

main().catch(console.error);
