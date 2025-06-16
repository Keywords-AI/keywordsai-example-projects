# Mastra Weather Agent with KeywordsAI Observability

A quick setup guide for running a Mastra weather agent with KeywordsAI telemetry integration.

## Setup

### 1. Install Dependencies

```bash
pnpm install
```

The project includes the required `@keywordsai/exporter-vercel` package for telemetry export.

### 2. Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.local.example .env.local
```

Update `.env.local` with your credentials:

```env
OPENAI_API_KEY=your-openai-api-key
KEYWORDSAI_API_KEY=your-keywordsai-api-key
KEYWORDSAI_BASE_URL=https://api.keywordsai.co
```

### 3. Run the Project

```bash
mastra dev
```

This opens the Mastra playground where you can interact with the weather agent.

## Observability

The project is configured with KeywordsAI telemetry in `src/mastra/index.ts`:

```typescript
telemetry: {
  serviceName: "keywordai-mastra-example",
  enabled: true,
  export: {
    type: "custom",
    exporter: new KeywordsAIExporter({
      apiKey: process.env.KEYWORDSAI_API_KEY,
      baseUrl: process.env.KEYWORDSAI_BASE_URL,
      debug: true,
    })
  }
}
```

Interact with the agent in the playground and view traces in your KeywordsAI dashboard. 