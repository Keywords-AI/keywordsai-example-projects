import { KeywordsAITelemetry } from '@keywordsai/tracing';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

async function runInstrumentationDemo() {
    console.log("=== KeywordsAI Instrumentation Management Demo ===\n");

    const autoDiscoveryClient = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
        appName: "auto-discovery-demo",
        disabledInstrumentations: ['bedrock', 'chromaDB'], 
        logLevel: 'info'
    });

    await autoDiscoveryClient.initialize();
    console.log("✅ Auto-discovery client initialized\n");
    await autoDiscoveryClient.shutdown();

    const explicitClient = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
        appName: "explicit-modules-demo",
        instrumentModules: {},
        logLevel: 'info'
    });

    await explicitClient.initialize();
    console.log("✅ Explicit client initialized\n");
    await explicitClient.shutdown();

    class MyCustomInstrumentation {
        manuallyInstrument(module: any) {
            console.log("🔧 Custom instrumentation logic applied to module!");
        }
    }

    const customClient = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
        appName: "custom-module-demo",
        instrumentModules: {
            myCustomTool: new MyCustomInstrumentation(),
            anotherTool: { version: '1.0.0' }
        },
        logLevel: 'info'
    });

    await customClient.initialize();
    console.log("✅ Custom module client initialized\n");
    await customClient.shutdown();

    console.log("🎉 Instrumentation management demo completed.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runInstrumentationDemo().catch(console.error);
}

export { runInstrumentationDemo };
