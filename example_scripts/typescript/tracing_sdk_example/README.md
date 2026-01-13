# KeywordsAI Tracing SDK Examples

This directory contains comprehensive examples of how to use the `@keywordsai/tracing` SDK. These examples cover all core functionalities tested in the Tracing SDK reference directory.

## Prerequisites

- Node.js (v18 or higher)
- A KeywordsAI API Key (from [keywordsai.com](https://keywordsai.com))
- (Optional) AI Provider API Keys (OpenAI, Anthropic) for real API testing

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Configure environment variables in `.env`:
   ```env
   KEYWORDSAI_API_KEY=your_keywordsai_api_key
   KEYWORDSAI_BASE_URL=https://api.keywordsai.co
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Examples

### Core Functionality

#### 1. Basic Usage (`basic_usage.ts`)
Core concepts: `withWorkflow`, `withTask`.
```bash
npx tsx tracing_sdk_example/basic_usage.ts
```

#### 2. OpenAI Integration (`openai_integration.ts`)
Automatic instrumentation of the OpenAI SDK.
```bash
npx tsx tracing_sdk_example/openai_integration.ts
```

#### 3. Advanced Tracing (`advanced_tracing.ts`)
Agentic workflows with `withAgent`, `withTool`, and custom metadata.
```bash
npx tsx tracing_sdk_example/advanced_tracing.ts
```

### Instrumentation & Configuration

#### 4. Instrumentation Management (`instrumentation_management.ts`)
Disabling specific instrumentations, explicit module loading, and custom module support.
```bash
npx tsx tracing_sdk_example/instrumentation_management.ts
```

#### 5. Manual Instrumentation (`manual_instrumentation.ts`)
Explicit module instrumentation for Next.js and environments where dynamic imports don't work.
```bash
npx tsx tracing_sdk_example/manual_instrumentation.ts
```

### Span Management

#### 6. Manual Span Management (`span_management.ts`)
Using the `getClient()` API to manually update spans, add events, and record exceptions.
```bash
npx tsx tracing_sdk_example/span_management.ts
```

#### 7. Update Span (`update_span.ts`)
Advanced span updating with KeywordsAI-specific parameters.
```bash
npx tsx tracing_sdk_example/update_span.ts
```

#### 8. Span Buffering (`span_buffering.ts`)
Manual control over span creation, buffering, and batch processing.
```bash
npx tsx tracing_sdk_example/span_buffering.ts
```

### Advanced Features

#### 9. Noise Filtering (`noise_filtering.ts`)
Demonstrates how the SDK filters out auto-instrumentation noise (like pure HTTP calls) outside of user contexts.
```bash
npx tsx tracing_sdk_example/noise_filtering.ts
```

#### 10. Multi-Provider Tracing (`multi_provider.ts`)
Tracing across multiple AI providers (OpenAI + Anthropic) in a single workflow.
```bash
npx tsx tracing_sdk_example/multi_provider.ts
```

#### 11. Multi-Processor (`multi_processor.ts`)
Custom span processors with routing, filters, and multiple exporters.
```bash
npx tsx tracing_sdk_example/multi_processor.ts
```

### Comprehensive Examples

#### 12. Usage Example (`usage_example.ts`)
Comprehensive example using all utility functions: `startTracing`, `getClient`, `updateCurrentSpan`, `addSpanEvent`, `recordSpanException`, `setSpanStatus`, `withManualSpan`, and all decorators.
```bash
npx tsx tracing_sdk_example/usage_example.ts
```

#### 13. Simple OpenAI Test (`simple_openai_test.ts`)
Simple test demonstrating OpenAI integration with global instance pattern.
```bash
npx tsx tracing_sdk_example/simple_openai_test.ts
```

#### 14. Test Tracing (`test_tracing.ts`)
Comprehensive test with a multi-step workflow (joke creation, translation, signature generation).
```bash
npx tsx tracing_sdk_example/test_tracing.ts
```

## Key API Reference

| Feature | Description |
| --- | --- |
| `withWorkflow` | High-level grouping of tasks. |
| `withTask` | Discrete step within a workflow. |
| `withAgent` / `withTool` | Specialized for agentic patterns. |
| `getClient()` | Access manual span management methods. |
| `updateCurrentSpan` | Update name, attributes, status, and KeywordsAI params. |
| `addSpanEvent` | Add a timestamped event to the current span. |
| `recordSpanException` | Record an error on the current span. |
| `setSpanStatus` | Set span status (OK, ERROR). |
| `withManualSpan` | Create manual spans for custom operations. |
| `getSpanBufferManager` | Access manual span buffering and processing. |
| `startTracing` | Alternative initialization helper. |
| `addProcessor` | Add custom span processors with routing. |

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `KEYWORDSAI_API_KEY` - Your KeywordsAI API key (required)
- `KEYWORDSAI_BASE_URL` - KeywordsAI API base URL (default: https://api.keywordsai.co)
- `OPENAI_API_KEY` - OpenAI API key (optional, for OpenAI examples)
- `OPENAI_BASE_URL` - OpenAI API base URL (optional)
- `ANTHROPIC_API_KEY` - Anthropic API key (optional, for Anthropic examples)
