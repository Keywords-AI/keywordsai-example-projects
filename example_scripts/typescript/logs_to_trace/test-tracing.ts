import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';
import * as dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * KeywordsAI Tracing Test Script
 * 
 * To run this script, you need to create a .env file in this directory with the following variables:
 * 
 * KEYWORDSAI_API_KEY=your_keywordsai_api_key
 * KEYWORDSAI_BASE_URL=https://api.keywordsai.co
 * 
 * // Using Keywords AI as an LLM Gateway for tracing
 * OPENAI_API_KEY=your_keywordsai_api_key
 * OPENAI_BASE_URL=https://api.keywordsai.co/api
 * 
 * You can get your API key from the Keywords AI platform: https://platform.keywordsai.co/platform/api-keys
 */

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from the same directory as this script
dotenv.config({ path: path.join(__dirname, '.env'), override: true });

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    baseURL: process.env.OPENAI_BASE_URL
});

async function main() {
    console.log('🚀 Starting improved KeywordsAI tracing test...');
    
    const keywordsAi = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY,
        baseURL: process.env.KEYWORDSAI_BASE_URL,
        appName: 'pirate-joke-test',
        disableBatch: true,
        logLevel: 'info',
        instrumentModules: {
            openAI: OpenAI
        }
    });

    try {
        await keywordsAi.initialize();
        console.log('✅ SDK initialized');

        // Implementation of the Pirate Joke Workflow from the documentation
        const finalResult = await keywordsAi.withWorkflow({ name: 'joke_workflow' }, async () => {
            console.log('Starting Pirate Joke Workflow...');

            // Task 1: Joke Creation
            const joke = await keywordsAi.withTask({ name: 'joke_creation' }, async () => {
                console.log('Task: Creating joke...');
                const completion = await openai.chat.completions.create({
                    model: 'gpt-4o-mini',
                    messages: [{ role: 'user', content: 'Tell me a short joke about OpenTelemetry' }],
                    temperature: 0.7
                });
                return completion.choices[0].message.content;
            });

            // Task 2: Pirate Translation
            const pirateJoke = await keywordsAi.withTask({ name: 'pirate_joke_translation' }, async () => {
                console.log('Task: Translating to pirate...');
                const completion = await openai.chat.completions.create({
                    model: 'gpt-4o-mini',
                    messages: [{ role: 'user', content: `Translate this joke to pirate language: ${joke}` }],
                    temperature: 0.7
                });
                return completion.choices[0].message.content;
            });

            // Task 3: Signature Generation
            const signatureJoke = await keywordsAi.withTask({ name: 'signature_generation' }, async () => {
                console.log('Task: Generating signature...');
                const completion = await openai.chat.completions.create({
                    model: 'gpt-4o-mini',
                    messages: [{ role: 'user', content: `Add a creative pirate signature to this joke: ${pirateJoke}` }],
                    temperature: 0.7
                });
                return completion.choices[0].message.content;
            });

            return signatureJoke;
        });

        console.log('\n--- Final Result ---');
        console.log(finalResult);
        console.log('--------------------');

        console.log('\n✅ Test completed successfully');
    } catch (error) {
        console.error('❌ Test failed:', error);
    } finally {
        await keywordsAi.shutdown();
    }
}

main();
