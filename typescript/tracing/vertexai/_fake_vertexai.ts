interface UsageMetadata {
  promptTokenCount: number;
  candidatesTokenCount: number;
  totalTokenCount: number;
}

interface FakeModelOptions {
  generationConfig?: Record<string, unknown>;
  systemInstruction?: unknown;
  tools?: unknown[];
}

function usage(promptTokenCount: number, candidatesTokenCount: number): UsageMetadata {
  return {
    promptTokenCount,
    candidatesTokenCount,
    totalTokenCount: promptTokenCount + candidatesTokenCount,
  };
}

function textResponse(text: string, tokenUsage = usage(9, 11)) {
  return {
    candidates: [
      {
        finishReason: "STOP",
        content: {
          role: "model",
          parts: [{ text }],
        },
      },
    ],
    usageMetadata: tokenUsage,
  };
}

function functionCallResponse(name: string, args: Record<string, unknown>) {
  return {
    candidates: [
      {
        finishReason: "STOP",
        content: {
          role: "model",
          parts: [
            {
              functionCall: {
                id: `call_${name}`,
                name,
                args,
              },
            },
          ],
        },
      },
    ],
    usageMetadata: usage(14, 6),
  };
}

function requestText(request: unknown): string {
  if (typeof request === "string") return request;
  if (!request || typeof request !== "object") return "";
  const contents = (request as Record<string, unknown>).contents;
  if (typeof contents === "string") return contents;
  if (!Array.isArray(contents)) return JSON.stringify(contents ?? "");
  return contents
    .flatMap((content) => {
      if (!content || typeof content !== "object") return [];
      const parts = (content as Record<string, unknown>).parts;
      if (!Array.isArray(parts)) return [];
      return parts.map((part) =>
        part && typeof part === "object" && typeof (part as Record<string, unknown>).text === "string"
          ? (part as Record<string, string>).text
          : "",
      );
    })
    .filter(Boolean)
    .join("\n");
}

export class GenerativeModel {
  public generationConfig?: Record<string, unknown>;
  public model: string;
  public systemInstruction?: unknown;
  public tools?: unknown[];

  constructor(model = "gemini-2.0-flash", options: FakeModelOptions = {}) {
    this.model = model;
    this.generationConfig = options.generationConfig;
    this.systemInstruction = options.systemInstruction;
    this.tools = options.tools;
  }

  async generateContent(request: unknown) {
    if (this.model.includes("intentional-error")) {
      throw new Error("intentional Vertex AI example error");
    }

    const text = requestText(request);
    if (/weather|tool|function/i.test(text)) {
      return {
        response: functionCallResponse("lookup_weather", { city: "Tokyo" }),
      };
    }

    return {
      response: textResponse(`Fake Vertex AI response for: ${text || "empty prompt"}`),
    };
  }

  async generateContentStream(request: unknown) {
    const text = requestText(request);
    return {
      stream: (async function* streamChunks() {
        yield textResponse("Fake ");
        yield textResponse("Vertex ");
        yield textResponse("stream response.");
      })(),
      response: Promise.resolve(
        textResponse(`Fake Vertex stream response for: ${text || "empty prompt"}`, usage(16, 19)),
      ),
    };
  }

  startChat() {
    return new ChatSession(this);
  }
}

export class ChatSession {
  public model: GenerativeModel;

  constructor(model: GenerativeModel) {
    this.model = model;
  }

  async sendMessage(content: unknown) {
    const text = requestText(content);
    if (/weather|tool|function/i.test(text)) {
      return {
        response: functionCallResponse("lookup_weather", { city: "Tokyo" }),
      };
    }

    return {
      response: textResponse(`Fake Vertex chat response for: ${text || "empty prompt"}`, usage(10, 12)),
    };
  }

  async sendMessageStream(content: unknown) {
    const text = requestText(content);
    return {
      stream: (async function* streamChunks() {
        yield textResponse("Chat ");
        yield textResponse("stream ");
        yield textResponse("complete.");
      })(),
      response: Promise.resolve(
        textResponse(`Fake Vertex chat stream response for: ${text || "empty prompt"}`, usage(13, 17)),
      ),
    };
  }
}

export class VertexAI {
  getGenerativeModel(options: FakeModelOptions & { model?: string }) {
    return new GenerativeModel(options.model, options);
  }
}

export const FakeVertexAIModule = {
  ChatSession,
  GenerativeModel,
  VertexAI,
};
