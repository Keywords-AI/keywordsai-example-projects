import { KeywordsAITelemetry } from '@keywordsai/tracing';
import {
  SpanExporter,
  ReadableSpan,
} from '@opentelemetry/sdk-trace-base';
import { ExportResult, ExportResultCode } from '@opentelemetry/core';
import * as fs from 'fs';
import * as path from 'path';
import dotenv from 'dotenv';

dotenv.config();

/**
 * This example demonstrates multi-processor routing:
 * 1. Adding custom processors with different exporters
 * 2. Routing spans to specific processors by name
 * 3. Using custom filter functions
 * 4. Sending spans to multiple destinations
 */

// Custom file exporter
class FileExporter implements SpanExporter {
  private filepath: string;

  constructor(filepath: string) {
    this.filepath = filepath;
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  export(
    spans: ReadableSpan[],
    resultCallback: (result: ExportResult) => void
  ): void {
    try {
      const spanData = spans.map((span) => ({
        name: span.name,
        traceId: span.spanContext().traceId,
        spanId: span.spanContext().spanId,
        attributes: Object.fromEntries(
          Object.entries(span.attributes).map(([k, v]) => [k, String(v)])
        ),
        timestamp: new Date().toISOString(),
      }));

      fs.appendFileSync(
        this.filepath,
        spanData.map((s) => JSON.stringify(s)).join('\n') + '\n'
      );

      console.log(`[FileExporter] Wrote ${spans.length} spans to ${this.filepath}`);
      resultCallback({ code: ExportResultCode.SUCCESS });
    } catch (error) {
      console.error('[FileExporter] Error:', error);
      resultCallback({ code: ExportResultCode.FAILURE });
    }
  }

  shutdown(): Promise<void> {
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}

// Custom console exporter
class ConsoleExporter implements SpanExporter {
  private prefix: string;

  constructor(prefix: string = 'ConsoleExporter') {
    this.prefix = prefix;
  }

  export(
    spans: ReadableSpan[],
    resultCallback: (result: ExportResult) => void
  ): void {
    for (const span of spans) {
      console.log(`[${this.prefix}] Span: ${span.name}`);
      console.log(`  Trace ID: ${span.spanContext().traceId}`);
      console.log(`  Attributes:`, span.attributes);
    }
    resultCallback({ code: ExportResultCode.SUCCESS });
  }

  shutdown(): Promise<void> {
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}

const keywordsAi = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY || 'demo-key',
  baseURL: process.env.KEYWORDSAI_BASE_URL,
  appName: 'multi-processor-demo',
  logLevel: 'info',
});

async function runMultiProcessorDemo() {
    await keywordsAi.initialize();

    // Check if addProcessor is available
    if (typeof keywordsAi.addProcessor !== 'function') {
        console.log('⚠️  addProcessor() is not available in this SDK version');
        console.log('This feature may require a newer version of @keywordsai/tracing');
        await keywordsAi.shutdown();
        return;
    }

    // Add debug processor
    keywordsAi.addProcessor({
    exporter: new FileExporter('./debug-spans.jsonl'),
    name: 'debug',
  });

  // Add analytics processor
  keywordsAi.addProcessor({
    exporter: new ConsoleExporter('Analytics'),
    name: 'analytics',
  });

  // Add slow span processor with custom filter
  keywordsAi.addProcessor({
    exporter: new ConsoleExporter('SlowSpans'),
    name: 'slow',
    filter: (span) => {
      const duration = span.endTime[0] - span.startTime[0];
      return duration > 0.1; // seconds
    },
  });

  await keywordsAi.withWorkflow({ name: 'multi_processor_demo' }, async () => {
    // Normal task (default processor only)
    await keywordsAi.withTask({ name: 'normal_task' }, async () => {
      console.log('Executing normal task (default processor)');
      await new Promise((resolve) => setTimeout(resolve, 50));
    });

    // Debug task (debug processor only)
    await keywordsAi.withTask(
      {
        name: 'debug_task',
        processors: 'debug',
      },
      async () => {
        console.log('Executing debug task (debug processor)');
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
    );

    // Multi task (both debug and analytics)
    await keywordsAi.withTask(
      {
        name: 'multi_task',
        processors: ['debug', 'analytics'],
      },
      async () => {
        console.log('Executing multi task (debug + analytics processors)');
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
    );

    // Slow task (slow processor via filter)
    await keywordsAi.withTask(
      {
        name: 'slow_task',
        processors: 'slow',
      },
      async () => {
        console.log('Executing slow task (slow processor with filter)');
        await new Promise((resolve) => setTimeout(resolve, 200));
      }
    );
  });

  await keywordsAi.shutdown();
  console.log('Check debug-spans.jsonl for debug spans');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runMultiProcessorDemo().catch(console.error);
}

export { runMultiProcessorDemo };
