import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

/**
 * Manual instrumentation example - similar to Traceloop approach
 * This is especially useful for Next.js and other environments where
 * dynamic imports might not work properly
 */

async function runManualInstrumentationDemo() {
    // Try to import Anthropic if available
    let Anthropic: any = null;
    try {
        const anthropicModule = await import('@anthropic-ai/sdk');
        Anthropic = anthropicModule.default;
    } catch (e) {
        console.log('Anthropic SDK not available, skipping Anthropic instrumentation');
    }

    const keywordsAI = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || 'test-key',
        baseURL: process.env.KEYWORDSAI_BASE_URL || 'https://api.keywordsai.co',
        appName: 'manual-instrumentation-example',
        disableBatch: true,
        logLevel: 'info',
        traceContent: true,
        // Manual instrumentation - pass the actual imported modules
        instrumentModules: {
            openAI: OpenAI,
            ...(Anthropic ? { anthropic: Anthropic } : {}),
        }
    });

    const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY || 'test-key',
    });

    const anthropic = Anthropic ? new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY || 'test-key',
    }) : null;

    await keywordsAI.initialize();
    console.log('🚀 Starting Manual Instrumentation Demo\n');

    // Multi-provider workflow
    await keywordsAI.withWorkflow(
        { name: 'multi_provider_workflow', version: 1 },
        async () => {
            // OpenAI task
            const openaiResult = await keywordsAI.withTask(
                { name: 'openai_completion' },
                async () => {
                    try {
                        const completion = await openai.chat.completions.create({
                            messages: [{ role: 'user', content: 'What is the capital of France?' }],
                            model: 'gpt-3.5-turbo',
                            temperature: 0.1
                        });
                        return completion.choices[0].message.content;
                    } catch (e) {
                        console.log('  (OpenAI call simulated or failed)');
                        return 'Simulated OpenAI response';
                    }
                }
            );

            // Anthropic task (if available)
            const anthropicResult = anthropic ? await keywordsAI.withTask(
                { name: 'anthropic_completion' },
                async () => {
                    try {
                        const message = await anthropic.messages.create({
                            model: 'claude-3-haiku-20240307',
                            max_tokens: 100,
                            messages: [{ role: 'user', content: 'What is the capital of Germany?' }]
                        });
                        return message.content[0].type === 'text' ? message.content[0].text : '';
                    } catch (e) {
                        console.log('  (Anthropic call simulated or failed)');
                        return 'Simulated Anthropic response';
                    }
                }
            ) : 'Anthropic SDK not available';

            return {
                openai: openaiResult,
                anthropic: anthropicResult
            };
        }
    );

    console.log('\n🧹 Shutting down...');
    await keywordsAI.shutdown();
    console.log('✅ Manual instrumentation demo completed.');
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runManualInstrumentationDemo().catch(console.error);
}

export { runManualInstrumentationDemo };
