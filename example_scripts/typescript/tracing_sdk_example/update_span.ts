import { updateCurrentSpan, startTracing, getClient } from '@keywordsai/tracing';
import { withAgent } from '@keywordsai/tracing';
import { SpanStatusCode } from '@opentelemetry/api';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

/**
 * Example demonstrating advanced span updating with KeywordsAI parameters
 */

async function runUpdateSpanDemo() {
    return await withAgent(
        {
            name: 'advancedAgent',
            associationProperties: {
                userId: 'user123',
                sessionId: 'session456',
            },
        },
        async () => {
            console.log('Agent started...');
            
            // Update span with KeywordsAI-specific parameters
            console.log('Updating span with KeywordsAI parameters...');
            updateCurrentSpan({
                keywordsaiParams: {
                    model: 'gpt-4',
                    provider: 'openai',
                    temperature: 0.7,
                    max_tokens: 1000,
                    user_id: 'user123',
                    metadata: {
                        experiment: 'A/B-test-v1',
                        feature_flag: 'new_ui_enabled',
                    },
                },
                attributes: {
                    'custom.operation': 'llm_call',
                    'custom.priority': 'high',
                },
            });

            await new Promise((resolve) => setTimeout(resolve, 100));

            // Update span name and status during processing
            console.log('Updating span name and processing stage...');
            updateCurrentSpan({
                name: 'advancedAgent.processing',
                attributes: {
                    'processing.stage': 'analysis',
                },
            });

            // Simulate successful completion
            console.log('Marking span as completed...');
            updateCurrentSpan({
                status: SpanStatusCode.OK,
                statusDescription: 'Processing completed successfully',
                attributes: {
                    'processing.stage': 'completed',
                    'result.count': 42,
                },
            });

            return {
                result: 'Advanced processing completed',
                processed_items: 42,
                model_used: 'gpt-4',
            };
        }
    );
}

async function main() {
    console.log('Starting Update Span Demo\n');
    
    // Initialize tracing
    await startTracing({
        apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
        baseURL: process.env.KEYWORDSAI_BASE_URL,
        appName: 'update-span-demo',
        disableBatch: true,
        logLevel: 'info'
    });
    
    console.log('Tracing initialized\n');
    
    try {
        const result = await runUpdateSpanDemo();
        console.log('\nResult:', result);
    } catch (error) {
        console.error('Error:', error);
    } finally {
        // Shutdown and flush traces
        console.log('\nShutting down...');
        const client = getClient();
        if (client && typeof client.shutdown === 'function') {
            await client.shutdown();
        }
        console.log('Update span demo completed.');
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { runUpdateSpanDemo };
