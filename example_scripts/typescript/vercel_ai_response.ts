import { KeywordsAIExporter } from "../src/index.js";
import { BasicTracerProvider, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { trace, context } from "@opentelemetry/api";
import { AsyncHooksContextManager } from "@opentelemetry/context-async-hooks";
import { generateText, streamText } from "ai";
// 假设你已经在项目中扩展了 openai 对象或者这是一个自定义实例
// 如果是标准 SDK，这里可能需要 cast: (openai as any).responses
import { openai } from "@ai-sdk/openai"; 
import { config } from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// ============================================================================
// 1. 初始化 Context Manager (异步追踪核心)
// ============================================================================
const contextManager = new AsyncHooksContextManager();
contextManager.enable();
context.setGlobalContextManager(contextManager);

// ============================================================================
// 2. 配置 Exporter
// ============================================================================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
config({ path: path.resolve(__dirname, "../.env") });

const exporter = new KeywordsAIExporter({
  apiKey: process.env.KEYWORDSAI_API_KEY,
  debug: true, // 调试模式，便于观察发送情况
});

const provider = new BasicTracerProvider();
provider.addSpanProcessor(new SimpleSpanProcessor(exporter));
provider.register();

// ============================================================================
// 3. Response API 专用示例 (Tests 3-6)
// ============================================================================
async function main() {
  console.log("🚀 Starting Keywords AI [Response API] Example...");
  const tracer = trace.getTracer("keywords-ai-response-example");

  await tracer.startActiveSpan("response-api-demo", async (rootSpan) => {
    try {
      
      // ---------------------------------------------------------
      // 场景 1: 单次文本生成 (Standard Response)
      // 对应你的 [TEST 3]
      // ---------------------------------------------------------
      console.log("\n1️⃣  Testing Standard Response (generateText)...");
      
      const result = await generateText({
        // 核心：使用 .responses 变体来触发 Exporter 的自动识别逻辑
        // @ts-ignore (忽略 TS 检查，如果你的 openai 类型没更新)
        model: openai.responses('gpt-4o'), 
        prompt: "Give me a 5-word fun fact about space.",
        experimental_telemetry: {
          isEnabled: true,
          functionId: "test-3-response",
          metadata: {
            userId: "user-new-test-999",
            customer_email: "user@example.com",
            customer_name: "John Doe",
            conversationId: "conv-abc-123",
            // ⭐️ 最佳实践：显式标记，确保 100% 识别为 Response
            custom_log_type: "response" 
          }
        }
      });
      console.log(`✅ Output: ${result.text}`);


      // ---------------------------------------------------------
      // 场景 2: 流式响应 (Streaming Response)
      // 对应你的 [TEST 4/5] - 即使是流，也是 Response 业务
      // ---------------------------------------------------------
      console.log("\n2️⃣  Testing Streaming Response (streamText)...");
      
      const streamResult = await streamText({
        // @ts-ignore
        model: openai.responses('gpt-4o-mini'),
        prompt: "Count from 1 to 5.",
        experimental_telemetry: {
          isEnabled: true,
          functionId: "test-4-stream-response",
          metadata: {
            userId: "user-new-test-999",
            // ⭐️ 关键：即便是流，因为业务属性是 Function Response，所以标记为 response
            custom_log_type: "response" 
          }
        }
      });

      process.stdout.write("✅ Stream Output: ");
      for await (const chunk of streamResult.textStream) {
        process.stdout.write(chunk);
      }
      console.log("\n");


      // ---------------------------------------------------------
      // 场景 3: 结构化 JSON 生成 (Structured Object)
      // 对应你的 [TEST 6] - 这种最应该被归类为 Response
      // ---------------------------------------------------------
      console.log("\n3️⃣  Testing JSON/Structured Response...");
      
      // 注意：这里也可以用 generateObject，但如果用 generateText + json mode：
      const jsonResult = await generateText({
        // @ts-ignore
        model: openai.responses('gpt-4o-mini'),
        prompt: "Generate a JSON object with a 'color' and 'hex' field for red.",
        // 强制 JSON 模式，Exporter 会自动识别 gen_ai.usage.type
        // @ts-ignore
        mode: 'json', 
        experimental_telemetry: {
          isEnabled: true,
          functionId: "test-6-json-response",
          metadata: {
            userId: "user-new-test-999",
            custom_log_type: "response"
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

  console.log("\n⏳ Waiting for spans to be exported...");
  await new Promise((resolve) => setTimeout(resolve, 2000));
}

main().catch(console.error);
