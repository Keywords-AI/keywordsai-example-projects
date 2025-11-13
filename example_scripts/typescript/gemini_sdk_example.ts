import { GoogleGenAI } from "@google/genai";
const API_KEY = "IqgCLJqD.hsYv5N1n24tb2JpSjZAQZoIqbrRG9A67"
const genAI = new GoogleGenAI({
  apiKey: API_KEY,
  httpOptions: {
    baseUrl: "https://api.keywordsai.co/api/google/gemini",
  },
});

const response = await genAI.models.generateContent({
  model: "gemini-2.5-flash",
  contents: [{ role: "user", parts: [{ text: "What color is the sky?" }] }],
  config: {
    temperature: 0.9,
    topK: 1,
    topP: 1,
    maxOutputTokens: 2048,
  },
});

console.log(JSON.stringify(response, null, 2));