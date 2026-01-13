import { startTracing, withWorkflow, withTask, withTool } from '@keywordsai/tracing';
import dotenv from 'dotenv';

dotenv.config();

async function runNoiseFilteringDemo() {
    console.log("=== KeywordsAI Noise Filtering Demo ===\n");

    await startTracing({
        apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
        baseURL: process.env.KEYWORDSAI_BASE_URL || "https://api.keywordsai.co",
        appName: "noise-filtering-demo",
        logLevel: "debug",
    });

    console.log("📡 Scenario 1: Making a request OUTSIDE any context");
    console.log("(This should NOT generate a span that is sent to KeywordsAI)");
    try {
        await fetch('https://httpbin.org/get');
    } catch (e) {}

    console.log("\n🚀 Scenario 2: Making requests INSIDE a workflow context");
    console.log("(This SHOULD preserve the child spans)");

    await withWorkflow({ name: "noise_filtered_workflow" }, async () => {
        console.log("  In workflow...");
        
        await withTask({ name: "api_task" }, async () => {
            console.log("    Making API call in task...");
            try {
                await fetch('https://httpbin.org/json');
                console.log("    API call finished");
            } catch (e) {}
        });

        await withTool({ name: "utility_tool" }, async () => {
            console.log("    Running tool...");
            await new Promise(resolve => setTimeout(resolve, 100));
        });
    });

    console.log("\n✅ Noise filtering demo completed.");
    console.log("Check debug logs to see which spans were 'dropped' vs 'preserved'.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runNoiseFilteringDemo().catch(console.error);
}

export { runNoiseFilteringDemo };
