import { KeywordsAITelemetry } from '@keywordsai/tracing';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env'), override: true });

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
    baseURL: process.env.OPENAI_BASE_URL
});

async function main() {
    console.log('Starting KeywordsAI tracing test...');
    
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
        console.log('SDK initialized');

        // Pirate Joke Workflow
        const finalResult = await keywordsAi.withWorkflow({ name: 'joke_workflow' }, async () => {
            console.log('Starting Pirate Joke Workflow...');

            // Task 1: Joke Creation
            const joke = await keywordsAi.withTask({ name: 'joke_creation' }, async () => {
                console.log('Task: Creating joke...');
                try {
                    const completion = await openai.chat.completions.create({
                        model: 'gpt-4o-mini',
                        messages: [{ role: 'user', content: 'Tell me a short joke about OpenTelemetry' }],
                        temperature: 0.7
                    });
                    return completion.choices[0].message.content;
                } catch (e) {
                    console.log('  (Simulated joke creation)');
                    return 'Why did the OpenTelemetry span cross the road? To trace the other side!';
                }
            });

            // Task 2: Pirate Translation
            const pirateJoke = await keywordsAi.withTask({ name: 'pirate_joke_translation' }, async () => {
                console.log('Task: Translating to pirate...');
                try {
                    const completion = await openai.chat.completions.create({
                        model: 'gpt-4o-mini',
                        messages: [{ role: 'user', content: `Translate this joke to pirate language: ${joke}` }],
                        temperature: 0.7
                    });
                    return completion.choices[0].message.content;
                } catch (e) {
                    console.log('  (Simulated pirate translation)');
                    return `Arrr! ${joke}`;
                }
            });

            // Task 3: Signature Generation
            const signatureJoke = await keywordsAi.withTask({ name: 'signature_generation' }, async () => {
                console.log('Task: Generating signature...');
                try {
                    const completion = await openai.chat.completions.create({
                        model: 'gpt-4o-mini',
                        messages: [{ role: 'user', content: `Add a creative pirate signature to this joke: ${pirateJoke}` }],
                        temperature: 0.7
                    });
                    return completion.choices[0].message.content;
                } catch (e) {
                    console.log('  (Simulated signature generation)');
                    return `${pirateJoke}\n\n- Captain Tracebeard`;
                }
            });

            return signatureJoke;
        });

        console.log('\n--- Final Result ---');
        console.log(finalResult);
        console.log('--------------------');

        console.log('\nTest completed successfully');
    } catch (error) {
        console.error('Test failed:', error);
    } finally {
        await keywordsAi.shutdown();
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { main };
