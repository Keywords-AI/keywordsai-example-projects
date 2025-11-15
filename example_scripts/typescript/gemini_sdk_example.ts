import { GoogleGenAI } from "@google/genai";
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from parent directory (example_scripts/.env)
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const API_KEY = process.env.KEYWORDSAI_API_KEY;
if (!API_KEY) {
  throw new Error("KEYWORDSAI_API_KEY not found in environment variables. Please set it in .env file.");
}

const genAI = new GoogleGenAI({
  apiKey: API_KEY,
  httpOptions: {
    baseUrl: "https://api.keywordsai.co/api/google/gemini",
  },
});

// Example: Comprehensive GenerateContentConfig showcasing various parameters
const response = await genAI.models.generateContent({
  model: "gemini-2.5-flash",
  contents: [
    { 
      role: "user", 
      parts: [{ text: "Who won the euro 2024?" }] 
    }
  ],
  config: {
    // System instruction to guide the model's behavior
    systemInstruction: "You are a helpful assistant that provides accurate, concise information about sports events.",
    
    // Sampling parameters
    temperature: 0.7, // Controls randomness (0.0-1.0). Lower = more focused, Higher = more creative
    topP: 0.95, // Nucleus sampling. Tokens with cumulative probability up to this value are considered
    topK: 40, // Top-k sampling. Considers this many top tokens at each step
    
    // Output controls
    maxOutputTokens: 1024, // Maximum number of tokens in the response
    stopSequences: ["\n\n\n"], // Sequences that will stop generation
    
    // Tools and function calling
    tools: [
      {
        googleSearch: {} // Enable Google Search grounding
      }
    ],
    
    // Thinking configuration (for models that support it)
    thinkingConfig: {
      thinkingBudget: 0 // Disables thinking mode
    },
    
    // Response format options
    // responseMimeType: "application/json", // Uncomment for JSON output
    // responseSchema: { // Uncomment to enforce structured output
    //   type: "object",
    //   properties: {
    //     winner: { type: "string" },
    //     year: { type: "integer" }
    //   }
    // },
    
    // Safety settings
    safetySettings: [
      {
        category: "HARM_CATEGORY_HATE_SPEECH",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        category: "HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
      }
    ],
    
    // Diversity controls
    presencePenalty: 0.0, // Penalize tokens based on presence in text (-2.0 to 2.0)
    frequencyPenalty: 0.0, // Penalize tokens based on frequency in text (-2.0 to 2.0)
    
    // Reproducibility
    // seed: 42, // Uncomment to make responses more deterministic
    
    // Logprobs (for token analysis)
    // responseLogprobs: true, // Uncomment to get log probabilities
    // logprobs: 5, // Number of top candidate tokens to return logprobs for
  },
});

console.log(response.text);