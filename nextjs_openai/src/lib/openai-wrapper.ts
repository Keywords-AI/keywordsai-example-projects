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

// Create OpenAI instance lazily to ensure instrumentation is ready
let openai: OpenAI | null = null;

function getOpenAIInstance() {
  if (!openai) {
    console.log("🔧 Creating OpenAI instance after instrumentation is ready");
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

  console.log("🚀 Starting generateChatCompletion with KeywordsAI workflow");

  return await keywordsai.withWorkflow(
    {
      name: "generateChatCompletion",
    },
    async (params) => {
      try {
        console.log("🔧 Inside workflow, getting OpenAI instance...");
        // Get OpenAI instance after instrumentation is ready
        const openaiClient = getOpenAIInstance();
        
        console.log("📤 Making OpenAI API call with params:", {
          model: params.model,
          messagesCount: params.messages.length,
          temperature: params.temperature
        });
        
        const completion = await openaiClient.chat.completions.create({
          model: params.model,
          messages: params.messages,
          temperature: params.temperature,
        });

        console.log("✅ OpenAI API call completed successfully");

        const assistantMessage = completion.choices[0]?.message?.content;
        return {
          message: assistantMessage,
          usage: completion.usage,
          model: completion.model,
          id: completion.id,
        };
      } catch (error) {
        console.error("❌ OpenAI API error:", error);
        throw error;
      }
    },
    {
      messages: messages,
      model: "gpt-4o-mini",
      temperature: 0.7,
    }
  );
}
