# KeywordsAI Tracing with Next.js and AI SDK Tutorial

This tutorial shows how to set up [KeywordsAI](https://docs.keywordsai.co/integration/development-frameworks/vercel-tracing) tracing with [Next.js](https://nextjs.org/) and the [AI SDK](https://ai-sdk.dev/docs) to monitor and trace your AI-powered applications.

## Deploy your own

Deploy the example using [Vercel](https://vercel.com?utm_source=github&utm_medium=readme&utm_campaign=ai-sdk-example):

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FKeywords-AI%2Fkeywordsai-example-projects%2Ftree%2Fmain%2Fvercel_ai_next_openai&env=OPENAI_API_KEY,KEYWORDSAI_API_KEY&project-name=keywordsai-next-tracing&repository-name=keywordsai-next-tracing)

---

## Choose Your Setup Method

You have two options to get started:

### Option 1: Use the Completed Example (Recommended)

Get up and running quickly with our pre-configured example:

```bash
npx create-next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_openai my-keywordsai-app
```

```bash
yarn create next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_openai my-keywordsai-app
```

```bash
pnpm create next-app --example https://github.com/Keywords-AI/keywordsai-example-projects/tree/main/vercel_ai_next_openai my-keywordsai-app
```

Then:
1. Add your API keys to `.env.local` (see [Step 3](#step-3-configure-environment-variables) below)
2. Run `yarn dev` to start the development server
3. Start chatting and check your [KeywordsAI dashboard](https://platform.keywordsai.co/platform/traces?page=1)

### Option 2: Follow the Step-by-Step Tutorial

If you want to understand the setup process or add KeywordsAI tracing to an existing project, follow the tutorial below.

Execute [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app) with [npm](https://docs.npmjs.com/cli/init), [Yarn](https://yarnpkg.com/lang/en/docs/cli/create/), or [pnpm](https://pnpm.io) to bootstrap the base example:

```bash
npx create-next-app --example https://github.com/vercel/ai/tree/main/examples/next-openai next-openai-app
```

```bash
yarn create next-app --example https://github.com/vercel/ai/tree/main/examples/next-openai next-openai-app
```

```bash
pnpm create next-app --example https://github.com/vercel/ai/tree/main/examples/next-openai next-openai-app
```

To run the base example locally you need to:

1. Sign up at [OpenAI's Developer Platform](https://platform.openai.com/signup).
2. Go to [OpenAI's dashboard](https://platform.openai.com/account/api-keys) and create an API KEY.
3. If you choose to use external files for attachments, then create a [Vercel Blob Store](https://vercel.com/docs/storage/vercel-blob).
4. Set the required environment variable as the token value as shown [the example env file](./.env.local.example) but in a new file called `.env.local`
5. `pnpm install` to install the required dependencies.
6. `pnpm dev` to launch the development server.

### KeywordsAI Telemetry Setup

Now let's add KeywordsAI tracing to monitor your AI application's performance and usage.

### Step 1: Install KeywordsAI Exporter

Install the KeywordsAI exporter package:

npm 
```bash
npm install @keywordsai/exporter-vercel
```
yarn 
```bash
yarn add @keywordsai/exporter-vercel
```
pnpm 
```bash
pnpm add @keywordsai/exporter-vercel
```

### Step 2: Set up OpenTelemetry Instrumentation

Next.js supports OpenTelemetry instrumentation out of the box. Following the [Next.js OpenTelemetry guide](https://nextjs.org/docs/app/guides/open-telemetry), create an `instrumentation.ts` file in your project root:

Install vercel's opentelemetry instrumentation

```bash
yarn add @vercel/otel
```

Create instrumentation.ts in the root (where package.json lives) of your project
```typescript
// instrumentation.ts
import { registerOTel } from "@vercel/otel";
import { KeywordsAIExporter } from "@keywordsai/exporter-vercel";

export function register() {
  registerOTel({
    serviceName: "next-app",
    traceExporter: new KeywordsAIExporter({ // <---- Use Keywords AI exporter as the custom exporter
      apiKey: process.env.KEYWORDSAI_API_KEY,
      baseUrl: process.env.KEYWORDSAI_BASE_URL,
      debug: true
    }),
  });
}
```

### Step 3: Configure Environment Variables

Add your KeywordsAI credentials to your `.env.local` file:

```env
# OpenAI API Key (existing)
OPENAI_API_KEY=your_openai_api_key_here

# KeywordsAI Configuration
KEYWORDSAI_API_KEY=your_keywordsai_api_key_here
KEYWORDSAI_BASE_URL=https://api.keywordsai.co  # Optional: defaults to KeywordsAI API
```

### Step 4: Enable Telemetry in API Routes

In your API route files (e.g., `app/api/chat/route.ts`), enable telemetry by adding the `experimental_telemetry` option to your AI SDK functions:

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages, id } = await req.json();

  console.log('chat id', id);

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    async onFinish({ text, toolCalls, toolResults, usage, finishReason }) {
      // implement your own logic here, e.g. for storing messages
      // or recording token usage
    },
    experimental_telemetry: {
      isEnabled: true,  // <---- Enable telemetry tracking
    },
  });

  return result.toDataStreamResponse();
}
```

### Step 5: Test Your Setup

1. Start your development server:
   ```bash
   yarn dev
   ```

**CAVEAT 2025-06-14**: There might be broken dependencies in the @vercel/otel package, simply install them if you see them:

```bash
yarn add @opentelementry/api-logs
```

If this fails, make sure you are use the right version of package manager
```json
// In package.json, add this line
"packageManager" : "yarn@4.9.2"
```
And try again


2. Make some chat requests through your application

3. Check your [KeywordsAI application](https://platform.keywordsai.co/platform/traces?page=1):
   - Go to Signals -> Traces
   - Check the log that is traced

## What Gets Traced

With this setup, KeywordsAI will automatically capture:

- **AI Model Calls**: All calls to OpenAI models through the AI SDK
- **Request/Response Data**: Input messages and generated responses
- **Token Usage**: Input and output token counts for cost tracking
- **Performance Metrics**: Latency and throughput data
- **Error Tracking**: Failed requests and error details
- **Custom Metadata**: Any additional context you want to track

## Learn More

To learn more about the technologies used in this tutorial:

- [KeywordsAI Documentation](https://docs.keywordsai.co) - learn about KeywordsAI features and tracing capabilities
- [AI SDK docs](https://ai-sdk.dev/docs) - comprehensive AI SDK documentation
- [Next.js OpenTelemetry Guide](https://nextjs.org/docs/app/guides/open-telemetry) - official Next.js telemetry documentation
- [Vercel AI Playground](https://ai-sdk.dev/playground) - test AI models interactively
- [OpenAI Documentation](https://platform.openai.com/docs) - learn about OpenAI features and API
- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
