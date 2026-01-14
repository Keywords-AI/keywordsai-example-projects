import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

async function runMultiProviderDemo() {
    console.log('✅ OpenAI and Anthropic SDKs loaded');

    const keywordsAi = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
        appName: "multi-provider-demo",
        // Use automatic discovery instead of manual instrumentation
        disableBatch: true,
        logLevel: 'info'
    });

    const openai = new OpenAI({ 
        apiKey: process.env.OPENAI_API_KEY || "test-key",
        baseURL: process.env.OPENAI_BASE_URL
    });
    const anthropic = new Anthropic({ 
        apiKey: process.env.ANTHROPIC_API_KEY || "test-key",
        baseURL: process.env.ANTHROPIC_BASE_URL
    });

    await keywordsAi.initialize();
    console.log("🚀 Starting Multi-Provider Demo\n");

    await keywordsAi.withWorkflow({ name: "multi_llm_workflow" }, async () => {
        
        console.log("🤖 Calling OpenAI...");
        await keywordsAi.withTask({ name: "openai_step" }, async () => {
            try {
                const response = await openai.chat.completions.create({
                    model: "gpt-3.5-turbo",
                    messages: [{ role: "user", content: "Hi" }]
                });
                console.log("  ✅ OpenAI response received:", response.choices[0]?.message?.content || "empty");
            } catch (e: any) {
                console.log("  ⚠️ OpenAI call failed:", e.message || e);
            }
        });

        console.log("🤖 Calling Anthropic...");
        await keywordsAi.withTask({ name: "anthropic_step" }, async () => {
            try {
                const response = await anthropic.messages.create({
                    model: "claude-3-haiku-20240307",
                    max_tokens: 10,
                    messages: [{ role: "user", content: "Hi" }]
                });
                console.log("  ✅ Anthropic response received:", response.content[0]);
            } catch (e: any) {
                console.log("  ⚠️ Anthropic call failed:", e.message || e);
            }
        });
    });

    console.log("\n🧹 Shutting down...");
    await keywordsAi.shutdown();
    console.log("✅ Multi-provider demo completed.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runMultiProviderDemo().catch(console.error);
}

export { runMultiProviderDemo };
