import { KeywordsAITelemetry } from '@keywordsai/tracing';
import { updateCurrentSpan, addSpanEvent } from '@keywordsai/tracing';
import * as fs from 'fs';
import * as path from 'path';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

/**
 * This example demonstrates span tracking and custom logging:
 * 1. Tracking different types of tasks (normal, debug, analytics, slow)
 * 2. Adding custom attributes and events
 * 3. Logging span information to files and console
 * 4. Demonstrating workflow with multiple task types
 * 
 * Note: This is a simplified version since addProcessor() API is not available
 */

// Helper to log span information to file
function logSpanToFile(filepath: string, spanInfo: any) {
  try {
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.appendFileSync(filepath, JSON.stringify(spanInfo) + '\n');
    console.log(`  Logged to ${filepath}`);
  } catch (error) {
    console.error('  File logging error:', error);
  }
}

// Helper to log span information to console
function logSpanToConsole(prefix: string, spanInfo: any) {
  console.log(`  [${prefix}] ${spanInfo.name} - ${spanInfo.type}`);
}

async function runMultiProcessorDemo() {
  console.log('Starting Span Tracking & Logging Demo\n');

  const keywordsAi = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
    baseURL: process.env.KEYWORDSAI_BASE_URL,
    appName: 'span-tracking-demo',
    logLevel: 'info',
    disableBatch: true,
  });

  await keywordsAi.initialize();
  console.log('Tracing initialized\n');

  await keywordsAi.withWorkflow({ name: 'span_tracking_workflow' }, async () => {
    // Normal task - standard tracing
    console.log('1. Normal Task:');
    await keywordsAi.withTask({ name: 'normal_task' }, async () => {
      updateCurrentSpan({
        attributes: {
          'task.type': 'normal',
          'task.priority': 'medium',
        },
      });
      addSpanEvent('task.started', { timestamp: Date.now() });
      await new Promise((resolve) => setTimeout(resolve, 50));
      addSpanEvent('task.completed', { timestamp: Date.now() });
      console.log('  Completed (standard tracing)');
    });

    // Debug task - with debug logging
    console.log('\n2. Debug Task:');
    await keywordsAi.withTask({ name: 'debug_task' }, async () => {
      const startTime = Date.now();
      updateCurrentSpan({
        attributes: {
          'task.type': 'debug',
          'task.priority': 'low',
          'debug.enabled': true,
        },
      });
      addSpanEvent('debug.started', { level: 'verbose' });
      
      await new Promise((resolve) => setTimeout(resolve, 50));
      
      const spanInfo = {
        name: 'debug_task',
        type: 'debug',
        duration: Date.now() - startTime,
        timestamp: new Date().toISOString(),
      };
      
      logSpanToFile('./debug-spans.jsonl', spanInfo);
      addSpanEvent('debug.logged', { file: 'debug-spans.jsonl' });
      console.log('  Completed (logged to file)');
    });

    // Analytics task - with console analytics
    console.log('\n3. Analytics Task:');
    await keywordsAi.withTask({ name: 'analytics_task' }, async () => {
      const startTime = Date.now();
      updateCurrentSpan({
        attributes: {
          'task.type': 'analytics',
          'task.priority': 'high',
          'analytics.enabled': true,
        },
      });
      addSpanEvent('analytics.started', { metrics: 'enabled' });
      
      await new Promise((resolve) => setTimeout(resolve, 80));
      
      const spanInfo = {
        name: 'analytics_task',
        type: 'analytics',
        duration: Date.now() - startTime,
        metrics: { processed: 42, errors: 0 },
        timestamp: new Date().toISOString(),
      };
      
      logSpanToConsole('Analytics', spanInfo);
      logSpanToFile('./analytics-spans.jsonl', spanInfo);
      addSpanEvent('analytics.completed', { records: 42 });
      console.log('  Completed (logged to console & file)');
    });

    // Slow task - demonstrates long-running operation
    console.log('\n4. Slow Task (long-running):');
    await keywordsAi.withTask({ name: 'slow_task' }, async () => {
      const startTime = Date.now();
      updateCurrentSpan({
        attributes: {
          'task.type': 'slow',
          'task.priority': 'low',
          'performance.warning': true,
        },
      });
      addSpanEvent('slow.task.started', { expected_duration: '200ms' });
      
      await new Promise((resolve) => setTimeout(resolve, 200));
      
      const duration = Date.now() - startTime;
      const spanInfo = {
        name: 'slow_task',
        type: 'slow',
        duration,
        warning: duration > 100 ? 'Exceeded threshold' : null,
        timestamp: new Date().toISOString(),
      };
      
      logSpanToConsole('SlowSpans', spanInfo);
      logSpanToFile('./slow-spans.jsonl', spanInfo);
      addSpanEvent('slow.task.completed', { actual_duration: duration });
      console.log(`  Completed in ${duration}ms (performance logged)`);
    });
  });

  console.log('\nShutting down...');
  await keywordsAi.shutdown();
  console.log('Span tracking demo completed.');
  console.log('\nCheck these files for logged spans:');
  console.log('   - ./debug-spans.jsonl');
  console.log('   - ./analytics-spans.jsonl');
  console.log('   - ./slow-spans.jsonl');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runMultiProcessorDemo().catch(console.error);
}

export { runMultiProcessorDemo, logSpanToFile, logSpanToConsole };
