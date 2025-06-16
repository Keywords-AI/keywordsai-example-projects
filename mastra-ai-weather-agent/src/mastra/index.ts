import { Mastra } from '@mastra/core';
import dotenv from 'dotenv';
import { weatherAgent } from './agents';
import { weatherWorkflow as legacyWeatherWorkflow } from './workflows';
import { weatherWorkflow, weatherWorkflow2 } from './workflows/new-workflow';
import { KeywordsAIExporter } from '@keywordsai/exporter-vercel';

dotenv.config({
  path: '.env.local',
  override: true,
});

export const mastra = new Mastra({
  agents: { weatherAgent },
  legacy_workflows: { legacyWeatherWorkflow },
  workflows: { weatherWorkflow, weatherWorkflow2 },
  telemetry: {
    serviceName: "keywordai-mastra-example",
    enabled: true,
    export: {
      type: "custom",
      "exporter": new KeywordsAIExporter({
        apiKey: process.env.KEYWORDSAI_API_KEY,
        baseUrl: process.env.KEYWORDSAI_BASE_URL,
        debug: true,
      })
    }
  }
});
