import { streamText, streamObject, generateText, tool } from "ai";
import { createOpenAI, openai } from "@ai-sdk/openai";
import { z } from "zod";
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from parent directory (example_scripts/.env)
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// Keywords AI parameters to be sent in the header
const keywordsAIHeaderContent = {
    "customer_identifier": "test_customer_identifier_from_header"
}
const encoded = Buffer.from(JSON.stringify(keywordsAIHeaderContent)).toString('base64');

const API_KEY = process.env.KEYWORDSAI_API_KEY;
if (!API_KEY) {
  throw new Error("KEYWORDSAI_API_KEY not found in environment variables. Please set it in .env file.");
}

const client = createOpenAI({
  headers: {
    "X-Data-Keywordsai-Params": encoded
  },
  baseURL: process.env.KEYWORDSAI_ENDPOINT_LOCAL || "https://api.keywordsai.co/api",
  apiKey: API_KEY,
});



const result = await generateText({
  model: client.responses('gpt-4o-mini'),
  prompt: 'What happened in San Francisco last week?',
  tools: {
    web_search_preview: client.tools.webSearchPreview({
      searchContextSize: 'high',
      userLocation: {
        type: 'approximate',
        city: 'San Francisco',
        region: 'California',
      },
    }),
  },
});

console.log(result.text);console.log(result.sources);
