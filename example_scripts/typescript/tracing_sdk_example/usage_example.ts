import {
  startTracing,
  getClient,
  getCurrentSpan,
  updateCurrentSpan,
  addSpanEvent,
  recordSpanException,
  setSpanStatus,
  withManualSpan,
} from '@keywordsai/tracing';
import {
  withWorkflow,
  withTask,
  withTool,
  withAgent,
} from '@keywordsai/tracing';
import dotenv from 'dotenv';

dotenv.config();

// Initialize tracing
startTracing({
  appName: 'my-ai-app',
  apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
  baseURL: process.env.KEYWORDSAI_BASE_URL || 'https://api.keywordsai.co',
  traceContent: true,
  logLevel: 'info',
});

// Example 1: Using decorators for automatic tracing
async function processDocument(document: string) {
  return withWorkflow(
    { name: 'document-processing' },
    async (doc: string) => {
      console.log('Processing document:', doc);

      const summary = await withTask(
        { name: 'summarize' },
        async (text: string) => {
          updateCurrentSpan({
            attributes: {
              'document.length': text.length,
              'document.type': 'text',
            },
          });

          addSpanEvent('summarization.started', {
            model: 'gpt-4',
            max_tokens: 150,
          });

          await new Promise((resolve) => setTimeout(resolve, 100));

          return `Summary of: ${text.substring(0, 50)}...`;
        },
        doc
      );

      const isValid = await withTool(
        { name: 'validate-summary' },
        async (summary: string) => {
          if (summary.length < 10) {
            const error = new Error('Summary too short');
            recordSpanException(error);
            setSpanStatus('ERROR', 'Summary validation failed');
            throw error;
          }

          setSpanStatus('OK', 'Summary validated successfully');
          return true;
        },
        summary
      );

      return { summary, isValid };
    },
    document
  );
}

// Example 2: Using manual spans
async function customOperation() {
  return withManualSpan(
    'custom-database-query',
    async (span) => {
      span.setAttribute('db.operation', 'SELECT');
      span.setAttribute('db.table', 'documents');

      await new Promise((resolve) => setTimeout(resolve, 50));

      span.addEvent('query.executed', {
        'rows.returned': 42,
      });

      return { count: 42, data: ['doc1', 'doc2'] };
    },
    {
      'service.name': 'document-service',
      'service.version': '1.0.0',
    }
  );
}

// Example 3: Agent-based processing
async function aiAgent(userQuery: string) {
  return withAgent(
    {
      name: 'customer-support-agent',
      version: 1,
      associationProperties: {
        'user.id': 'user123',
        'session.id': 'session456',
      },
    },
    async (query: string) => {
      const context = await withTool(
        { name: 'retrieve-context' },
        async (q: string) => {
          updateCurrentSpan({
            attributes: {
              'search.query': q,
              'search.type': 'semantic',
            },
          });
          return `Context for: ${q}`;
        },
        query
      );

      const response = await withTool(
        { name: 'generate-response' },
        async (ctx: string) => {
          addSpanEvent('llm.call.started', {
            model: 'gpt-4',
            temperature: 0.7,
          });

          await new Promise((resolve) => setTimeout(resolve, 200));

          addSpanEvent('llm.call.completed', {
            'tokens.used': 150,
            'cost.usd': 0.003,
          });

          return `AI Response based on: ${ctx}`;
        },
        context
      );

      return response;
    },
    userQuery
  );
}

// Example 4: Error handling
async function errorProneOperation() {
  try {
    return withWorkflow({ name: 'risky-operation' }, async () => {
      const currentSpan = getCurrentSpan();
      console.log('Current span:', currentSpan?.spanContext().spanId);

      const client = getClient();
      console.log('SDK initialized:', !!client);

      const random = Math.random();
      if (random < 0.3) {
        throw new Error('Random failure occurred');
      }

      updateCurrentSpan({
        attributes: {
          'operation.success': true,
          'random.value': random,
        },
      });

      return { success: true, value: random };
    });
  } catch (error) {
    console.error('Operation failed:', error);
    throw error;
  }
}

async function main() {
  try {
    console.log('=== Document Processing Example ===');
    const result1 = await processDocument(
      'This is a sample document that needs to be processed and summarized.'
    );
    console.log('Result:', result1);

    console.log('\n=== Custom Operation Example ===');
    const result2 = await customOperation();
    console.log('Result:', result2);

    console.log('\n=== AI Agent Example ===');
    const result3 = await aiAgent('How can I reset my password?');
    console.log('Result:', result3);

    console.log('\n=== Error Handling Example ===');
    for (let i = 0; i < 3; i++) {
      try {
        const result4 = await errorProneOperation();
        console.log(`Attempt ${i + 1} succeeded:`, result4);
        break;
      } catch (error) {
        console.log(`Attempt ${i + 1} failed:`, (error as Error).message);
      }
    }
  } catch (error) {
    console.error('Main execution failed:', error);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main()
    .then(() => {
      console.log('\nExample completed. Check your KeywordsAI dashboard for traces!');
    })
    .catch((error) => {
      console.error('Example failed:', error);
    });
}

export { processDocument, customOperation, aiAgent, errorProneOperation };
