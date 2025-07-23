# KeywordsAI Tracing Setup Guide

This guide shows how to add KeywordsAI tracing to your Next.js application with OpenAI integration. This setup initializes KeywordsAI directly in your OpenAI wrapper and only traces your model calls.

## Prerequisites

- A Next.js application with OpenAI integration
- KeywordsAI API key from [platform.keywordsai.co](https://platform.keywordsai.co)
- OpenAI API key

## Installation

### 1. Install Required Packages

```bash
yarn add @keywordsai/tracing dotenv
```

### 2. Environment Variables

Create a `.env.local` file in your project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here

KEYWORDSAI_API_KEY=your_keywordsai_api_key
KEYWORDSAI_BASE_URL=https://api.keywordsai.co
```

### 3. Create OpenAI Wrapper with Tracing

Create `src/lib/openai-wrapper.ts` with integrated KeywordsAI initialization:

```typescript
import OpenAI from "openai";
import { KeywordsAITelemetry } from "@keywordsai/tracing";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config({ path: ".env.local", override: true });

// Declare global type
declare global {
  var keywordsai: KeywordsAITelemetry | undefined;
}

// Initialize KeywordsAI telemetry once
let initPromise: Promise<void> | null = null;

async function initializeKeywordsAI() {
  if (global.keywordsai) return; // Already initialized
  
  if (!initPromise) {
    initPromise = (async () => {
      console.log("🔧 Initializing KeywordsAI telemetry...");
      const keywordsai = new KeywordsAITelemetry({
        apiKey: process.env.KEYWORDSAI_API_KEY || "",
        baseURL: process.env.KEYWORDSAI_BASE_URL || "",
        logLevel: "debug",
        instrumentModules: {
          openAI: OpenAI, // This enables OpenAI tracing
        },
        disableBatch: true,
      });
      
      await keywordsai.initialize();
      global.keywordsai = keywordsai;
      console.log("✅ KeywordsAI telemetry initialized");
    })();
  }
  
  return initPromise;
}

// Create OpenAI instance lazily
let openai: OpenAI | null = null;

function getOpenAIInstance() {
  if (!openai) {
    openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY || "",
    });
  }
  return openai;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export async function generateChatCompletion(messages: ChatMessage[]) {
  // Initialize telemetry before using it
  await initializeKeywordsAI();
  
  const keywordsai = global.keywordsai;
  
  if (!keywordsai) {
    throw new Error("KeywordsAI failed to initialize");
  }

  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async (params) => {
      const openaiClient = getOpenAIInstance();
      
      const completion = await openaiClient.chat.completions.create({
        model: params.model,
        messages: params.messages,
        temperature: params.temperature,
      });

      const assistantMessage = completion.choices[0]?.message?.content;
      return {
        message: assistantMessage,
        usage: completion.usage,
        model: completion.model,
        id: completion.id,
      };
    },
    {
      messages: messages,
      model: "gpt-4o-mini",
      temperature: 0.7,
    }
  );
}
```

### 4. Use in Your API Routes

In your API routes (e.g., `src/app/api/chat/route.ts`), import and use the wrapper:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { generateChatCompletion, ChatMessage } from '@/lib/openai-wrapper';

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    const validMessages: ChatMessage[] = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    const result = await generateChatCompletion(validMessages);

    return NextResponse.json({ 
      message: result.message,
      usage: result.usage,
      model: result.model,
      id: result.id
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Failed to get response from OpenAI' },
      { status: 500 }
    );
  }
}
```

### 5. Start Your Application

```bash
yarn dev
```

Visit your application and make OpenAI API calls. You'll see initialization logs in your console.

### 6. View Traces

Your traces will appear on the KeywordsAI platform at [platform.keywordsai.co](https://platform.keywordsai.co)

## How This Setup Works

1. **Lazy Initialization**: KeywordsAI telemetry initializes only when you first call `generateChatCompletion`
2. **Automatic Instrumentation**: The `instrumentModules.openAI` configuration automatically patches all OpenAI SDK calls
3. **Workflow Tracking**: Each function wrapped with `withWorkflow` creates a trace with the given name
4. **Global Instance**: The telemetry instance is stored globally and reused across all calls

## Key Benefits

- **Minimal Setup**: No separate instrumentation files needed
- **Model-Only Tracing**: Only traces your OpenAI calls, not Next.js internals
- **Environment Isolation**: Loads environment variables directly where needed
- **Lazy Loading**: Telemetry only initializes when actually used

## Configuration Options

You can customize the KeywordsAI initialization:

```typescript
const keywordsai = new KeywordsAITelemetry({
  apiKey: process.env.KEYWORDSAI_API_KEY || "",
  baseURL: process.env.KEYWORDSAI_BASE_URL || "",
  logLevel: "debug", // "debug" | "info" | "warn" | "error"
  instrumentModules: {
    openAI: OpenAI, // Required for OpenAI tracing
  },
  disableBatch: true, // Set to false to enable batching
});
```

## Troubleshooting

- **"KeywordsAI failed to initialize"**: Check your API key and base URL in `.env.local`
- **No traces appearing**: Verify your KeywordsAI API key and that you're calling the wrapped functions
- **Environment variables not loading**: Ensure `.env.local` is in your project root
