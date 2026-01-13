import { updateCurrentSpan } from '@keywordsai/tracing';
import { withAgent } from '@keywordsai/tracing';
import { SpanStatusCode } from '@opentelemetry/api';
import dotenv from 'dotenv';

dotenv.config();

/**
 * Example demonstrating advanced span updating with KeywordsAI parameters
 */

async function runUpdateSpanDemo() {
    return withAgent(
        {
            name: 'advancedAgent',
            associationProperties: {
                userId: 'user123',
                sessionId: 'session456',
            },
        },
        async () => {
            // Update span with KeywordsAI-specific parameters
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
            updateCurrentSpan({
                name: 'advancedAgent.processing',
                attributes: {
                    'processing.stage': 'analysis',
                },
            });

            // Simulate successful completion
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
    console.log('🚀 Starting Update Span Demo\n');
    try {
        const result = await runUpdateSpanDemo();
        console.log('Result:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { runUpdateSpanDemo };
