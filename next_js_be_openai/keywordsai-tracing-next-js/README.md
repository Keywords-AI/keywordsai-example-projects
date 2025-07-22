# KeywordsAI Tracing Setup Guide

This is a Next.js chatbot application with KeywordsAI tracing integration.

## Setup Instructions

### 1. Environment Variables

Create a `.env.local` file from the example:

```bash
cp .env.local.example .env.local
```

Update the values in `.env.local`:
```
OPENAI_API_KEY=your_openai_api_key_here

KEYWORDSAI_API_KEY=your_keywordsai_api_key
KEYWORDSAI_BASE_URL=https://api.keywordsai.co
```

### 2. Instrumentation Setup

In `src/instrumentation.ts`, initialize KeywordsAI:

```typescript
import { KeywordsAITelemetry } from "@keywordsai/tracing";

declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

export function register() {
  global.keywordsai = new KeywordsAITelemetry({
    apiKey: process.env.KEYWORDSAI_API_KEY || "",
    baseUrl: process.env.KEYWORDSAI_BASE_URL || "",
    logLevel: "debug",
    disableBatch: true,
  });
  global.keywordsai.initialize(); // Important: call initialize()
}
```

### 3. OpenAI Wrapper

In `src/lib/openai-wrapper.ts`, wrap your functions with KeywordsAI workflows:

```typescript
export async function generateChatCompletion(messages: ChatMessage[]) {
  const keywordsai = global.keywordsai;
  
  if (!keywordsai) {
    throw new Error("KeywordsAI not initialized.");
  }

  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion", // Workflow name
    },
    async () => {
      // Your OpenAI function logic here
    }
  );
}
```

### 4. Start the Application

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) and start chatting with the bot.

### 5. View Traces

Your traces will appear on the KeywordsAI platform at [platform.keywordsai.co](https://platform.keywordsai.co)

## Key Points

- The `instrumentation.ts` file automatically runs when Next.js starts
- Call `.initialize()` on the KeywordsAI instance
- Use `global.keywordsai` to access the telemetry instance in other files
- Wrap your functions with `withWorkflow` to trace them
- Each workflow needs a unique `name`
