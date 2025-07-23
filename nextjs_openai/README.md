# KeywordsAI Telemetry Integration

This project demonstrates how to integrate KeywordsAI telemetry with OpenAI in a Next.js application for automatic tracing of your AI model calls.

## Installation

```bash
yarn add @keywordsai/tracing
```

Keywords AI tracing SDK will be looking for instrumentations to initialize, we need to install the instrumentation too
```bash
yarn add @traceloop/instrumentation-openai
```

## Configuration

### Environment Variables

Add to your `.env.local`:

```bash
KEYWORDSAI_API_KEY=your_keywordsai_api_key
KEYWORDSAI_BASE_URL=https://api.keywordsai.co
OPENAI_API_KEY=your_openai_api_key
```

### Initialize KeywordsAI Telemetry

Create a dedicated initialization file to set up the KeywordsAI singleton:

**`src/lib/keywordsai-init.ts`:**
```typescript
import { KeywordsAITelemetry } from "@keywordsai/tracing";
import OpenAI from "openai";

const keywordsai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY || "",
  baseURL: process.env.KEYWORDSAI_BASE_URL || "",
  logLevel: "info", // This shows initialization logs for troubleshooting
  instrumentModules: {
    openAI: OpenAI,
  },
});

keywordsai.initialize();

export { keywordsai };
```

## Usage Example

Import the KeywordsAI instance and use it to wrap your functions:

```typescript
import { keywordsai } from "./keywordsai-init";

export async function generateChatCompletion(messages: ChatMessage[]) {
  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async (params: {
      messages: ChatMessage[];
      model: string;
      temperature: number;
    }) => {
      // Your OpenAI API call logic here
      // params.messages, params.model, params.temperature are available
      // ...
    },
    {
      messages: messages,
      model: "gpt-4o-mini", 
      temperature: 0.7,
    }
  );
}
```

## Complete Implementation

See the full implementation in [`src/lib/openai-wrapper.ts`](./src/lib/openai-wrapper.ts) and how it's used in the API route [`src/app/api/chat/route.ts`](./src/app/api/chat/route.ts).

## Run the Project

```bash
yarn dev
```

Visit the application and make chat requests. Your traces will appear on the KeywordsAI platform at [platform.keywordsai.co](https://platform.keywordsai.co)

## Key Benefits

- **Clean initialization** - Separate file for KeywordsAI setup
- **Simple usage** - Import the instance and use it anywhere
- **Proper instrumentation** - Avoids timing issues with automatic tracing

## Troubleshooting

### 🔍 Enable Debug Logging

For better troubleshooting, set the `logLevel` to see initialization logs:

```typescript
const keywordsai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY || "",
  baseURL: process.env.KEYWORDSAI_BASE_URL || "",
  logLevel: "info", // This shows initialization logs for troubleshooting
  instrumentModules: {
    openAI: OpenAI,
  },
});
```

**Log levels available:**
- `"debug"` - Most verbose, shows all internal operations
- `"info"` - Shows initialization status and key events  
- `"warn"` - Only warnings and errors
- `"error"` - Only errors

### ⚠️ Missing OpenAI Instrumentation Dependency

If you encounter initialization errors or OpenAI calls are not being traced, ensure you have installed the required instrumentation:

```bash
yarn add @traceloop/instrumentation-openai
```

**Why you need this:**
- KeywordsAI SDK looks for available instrumentations to initialize
- Without the OpenAI instrumentation package, OpenAI calls won't be traced
- This is a required peer dependency for OpenAI tracing to work

### ❌ Avoid Next.js Instrumentation File

**Do not** initialize KeywordsAI in Next.js's `instrumentation.ts` file:

```typescript
// ❌ DON'T DO THIS - This breaks OpenAI tracing
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./src/lib/keywordsai-init');
  }
}
```

**Why this doesn't work:**
- Next.js instrumentation runs very early in the application lifecycle
- This interferes with KeywordsAI's own OpenAI instrumentation timing
- Results in broken or missing traces for OpenAI API calls
- The traces will not capture OpenAI requests properly

**✅ Use the recommended approach instead:**
- Create a separate initialization file (`src/lib/keywordsai-init.ts`)
- Import the KeywordsAI instance where needed
- This ensures proper instrumentation timing and complete trace coverage
