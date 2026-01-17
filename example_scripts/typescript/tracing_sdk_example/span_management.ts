import { KeywordsAITelemetry, getClient } from '@keywordsai/tracing';
import { updateCurrentSpan, addSpanEvent, recordSpanException } from '@keywordsai/tracing';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "demo-key",
    appName: "span-management-demo",
    disableBatch: true,
    logLevel: 'info'
});

async function runSpanManagementDemo() {
    await keywordsAi.initialize();
    console.log("Starting Span Management Demo\n");

    await keywordsAi.withWorkflow({ name: "main_workflow" }, async () => {
        const client = getClient();
        
        // Check if methods exist before calling
        if (client && typeof client.getCurrentTraceId === 'function' && typeof client.getCurrentSpanId === 'function') {
            const traceId = client.getCurrentTraceId();
            const spanId = client.getCurrentSpanId();
            console.log(`Trace ID: ${traceId}`);
            console.log(`Span ID: ${spanId}`);
        } else {
            console.log('Trace/span ID methods not available in this SDK version');
        }

        console.log("Updating span attributes...");
        updateCurrentSpan({
            name: "main_workflow.executed",
            attributes: {
                "custom.status": "processing",
                "env": "test"
            },
            keywordsaiParams: {
                customerIdentifier: "user_999",
                traceGroupIdentifier: "demo-group",
                metadata: {
                    version: "2.0.0"
                }
            }
        });

        console.log("Adding an event...");
        addSpanEvent("data_fetch_started", {
            source: "cache",
            priority: "high"
        });

        await new Promise(resolve => setTimeout(resolve, 200));

        await keywordsAi.withTask({ name: "sub_task" }, async () => {
            console.log("In sub-task...");
            
            addSpanEvent("sub_task_event");
            
            console.log("Recording a simulated exception...");
            try {
                throw new Error("Something went wrong in the sub-task");
            } catch (e) {
                recordSpanException(e as Error);
            }
        });

        addSpanEvent("workflow_completed");
    });

    console.log("\nShutting down...");
    await keywordsAi.shutdown();
    console.log("Span management demo completed.");
}

if (import.meta.url === `file://${process.argv[1]}`) {
    runSpanManagementDemo().catch(console.error);
}

export { runSpanManagementDemo };
