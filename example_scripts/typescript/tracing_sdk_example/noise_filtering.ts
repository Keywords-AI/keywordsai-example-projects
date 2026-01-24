import { startTracing, withWorkflow, withTask, withTool, getClient } from '@keywordsai/tracing';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

async function runNoiseFilteringDemo() {
    console.log("=== KeywordsAI Noise Filtering Demo ===\n");

    await startTracing({
        apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
        baseURL: process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
        appName: "noise-filtering-demo",
        logLevel: "info",
        instrumentModules: {
            openAI: OpenAI
        }
    });

    const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY || 'test-key',
        baseURL: process.env.OPENAI_BASE_URL
    });

    console.log("Scenario 1: Making an OpenAI request OUTSIDE any context");
    console.log("(This should NOT be sent to KeywordsAI - filtered as noise)\n");
    try {
        await openai.chat.completions.create({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: 'Hi' }],
            max_tokens: 5
        });
        console.log("  OpenAI call completed (but span should be filtered)\n");
    } catch (e) {
        console.log("  OpenAI call failed or simulated\n");
    }

    console.log("Scenario 2: Making OpenAI requests INSIDE a workflow context");
    console.log("(Child spans SHOULD be preserved and sent to KeywordsAI)\n");

    await withWorkflow({ name: "noise_filtered_workflow" }, async () => {
        console.log("  Inside workflow context...\n");
        
        await withTask({ name: "llm_task" }, async () => {
            console.log("    Making OpenAI call inside task...");
            try {
                const response = await openai.chat.completions.create({
                    model: 'gpt-3.5-turbo',
                    messages: [{ role: 'user', content: 'Say hello' }],
                    max_tokens: 10
                });
                console.log(`    OpenAI response: ${response.choices[0]?.message?.content || 'N/A'}`);
                console.log("    This openai.chat span should be a CHILD of llm_task\n");
            } catch (e: any) {
                console.log(`    OpenAI call failed: ${e.message}\n`);
            }
        });

        await withTask({ name: "another_llm_task" }, async () => {
            console.log("    Making another OpenAI call...");
            try {
                const response = await openai.chat.completions.create({
                    model: 'gpt-3.5-turbo',
                    messages: [{ role: 'user', content: 'Count to 3' }],
                    max_tokens: 15
                });
                console.log(`    OpenAI response: ${response.choices[0]?.message?.content || 'N/A'}`);
                console.log("    This openai.chat span should be a CHILD of another_llm_task\n");
            } catch (e: any) {
                console.log(`    OpenAI call failed: ${e.message}\n`);
            }
        });

        await withTool({ name: "utility_tool" }, async () => {
            console.log("    Running utility tool (no LLM call)...");
            await new Promise(resolve => setTimeout(resolve, 50));
            console.log("    Utility completed\n");
        });
    });

    console.log("Noise filtering demo completed.");
    console.log("\nExpected trace structure:");
    console.log("   noise_filtered_workflow (workflow)");
    console.log("   +-- llm_task (task)");
    console.log("   |   +-- openai.chat (child span - PRESERVED)");
    console.log("   +-- another_llm_task (task)");
    console.log("   |   +-- openai.chat (child span - PRESERVED)");
    console.log("   +-- utility_tool (tool)");
    console.log("\n   Scenario 1 openai.chat span: FILTERED (not in trace)");
    
    console.log("\nShutting down...");
    const client = getClient();
    if (client && typeof client.shutdown === 'function') {
        await client.shutdown();
    }
    console.log("Shutdown complete.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runNoiseFilteringDemo().catch(console.error);
}

export { runNoiseFilteringDemo };
