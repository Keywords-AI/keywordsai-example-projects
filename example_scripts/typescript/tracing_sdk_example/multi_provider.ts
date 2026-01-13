import OpenAI from 'openai';
import { KeywordsAITelemetry } from '@keywordsai/tracing';
import dotenv from 'dotenv';

dotenv.config();

async function runMultiProviderDemo() {
    // Try to import Anthropic if available
    let Anthropic: any = null;
    try {
        const anthropicModule = await import('@anthropic-ai/sdk');
        Anthropic = anthropicModule.default;
    } catch (e) {
        console.log('Anthropic SDK not available, will skip Anthropic calls');
    }

    const keywordsAi = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
        appName: "multi-provider-demo",
        instrumentModules: {
            openAI: OpenAI,
            ...(Anthropic ? { anthropic: Anthropic } : {}),
        },
        disableBatch: true,
        logLevel: 'info'
    });

    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY || "test-key" });
    const anthropic = Anthropic ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY || "test-key" }) : null;

    await keywordsAi.initialize();
    console.log("🚀 Starting Multi-Provider Demo\n");

    await keywordsAi.withWorkflow({ name: "multi_llm_workflow" }, async () => {
        
        console.log("🤖 Calling OpenAI...");
        await keywordsAi.withTask({ name: "openai_step" }, async () => {
            try {
                await openai.chat.completions.create({
                    model: "gpt-3.5-turbo",
                    messages: [{ role: "user", content: "Hi" }]
                });
            } catch (e) {
                console.log("  (OpenAI call simulated or failed - tracing still active)");
            }
        });

        if (anthropic) {
            console.log("🤖 Calling Anthropic...");
            await keywordsAi.withTask({ name: "anthropic_step" }, async () => {
                try {
                    await anthropic.messages.create({
                        model: "claude-3-haiku-20240307",
                        max_tokens: 10,
                        messages: [{ role: "user", content: "Hi" }]
                    });
                } catch (e) {
                    console.log("  (Anthropic call simulated or failed - tracing still active)");
                }
            });
        } else {
            console.log("🤖 Skipping Anthropic (SDK not available)");
        }
    });

    console.log("\n🧹 Shutting down...");
    await keywordsAi.shutdown();
    console.log("✅ Multi-provider demo completed.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runMultiProviderDemo().catch(console.error);
}

export { runMultiProviderDemo };
