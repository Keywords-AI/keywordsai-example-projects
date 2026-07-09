import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

export interface TogetherMockServer {
  baseURL: string;
  close: () => Promise<void>;
}

export async function startTogetherMockServer(): Promise<TogetherMockServer> {
  const server = createServer(async (request, response) => {
    try {
      await handleRequest(request, response);
    } catch (error) {
      writeJson(response, 500, {
        error: { message: error instanceof Error ? error.message : String(error) },
      });
    }
  });

  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Failed to start Together AI mock server.");
  }

  return {
    baseURL: `http://127.0.0.1:${address.port}/v1`,
    close: () => new Promise((resolve, reject) => {
      server.close((error) => error ? reject(error) : resolve());
    }),
  };
}

async function handleRequest(request: IncomingMessage, response: ServerResponse): Promise<void> {
  const url = new URL(request.url ?? "/", "http://127.0.0.1");
  const body = await readBody(request);

  if (request.method !== "POST") {
    writeJson(response, 405, { error: { message: "Method not allowed" } });
    return;
  }

  if (url.pathname === "/v1/chat/completions") {
    const payload = parseJsonBody(body);
    if (String(payload.model ?? "").includes("nonexistent")) {
      writeJson(response, 404, { error: { message: "Model not found" } });
      return;
    }
    if (payload.stream === true) {
      writeSse(response, [
        {
          id: "chatcmpl_mock_stream",
          object: "chat.completion.chunk",
          created: Math.floor(Date.now() / 1000),
          model: payload.model,
          choices: [{ index: 0, delta: { role: "assistant", content: "Mock " }, finish_reason: null }],
        },
        {
          id: "chatcmpl_mock_stream",
          object: "chat.completion.chunk",
          created: Math.floor(Date.now() / 1000),
          model: payload.model,
          choices: [{ index: 0, delta: { content: "stream" }, finish_reason: "stop" }],
          usage: { prompt_tokens: 8, completion_tokens: 2, total_tokens: 10 },
        },
      ]);
      return;
    }

    const hasTools = Array.isArray(payload.tools) && payload.tools.length > 0;
    writeJson(response, 200, {
      id: "chatcmpl_mock",
      object: "chat.completion",
      created: Math.floor(Date.now() / 1000),
      model: payload.model,
      prompt: [],
      choices: [
        {
          index: 0,
          finish_reason: hasTools ? "tool_calls" : "stop",
          message: hasTools ? {
            role: "assistant",
            content: null,
            tool_calls: [
              {
                id: "call_mock_weather",
                type: "function",
                function: { name: "get_weather", arguments: JSON.stringify({ city: "Tokyo" }) },
              },
            ],
          } : {
            role: "assistant",
            content: "Mock Together AI chat response traced by Respan.",
          },
        },
      ],
      usage: { prompt_tokens: 11, completion_tokens: 7, total_tokens: 18 },
    });
    return;
  }

  if (url.pathname === "/v1/completions") {
    const payload = parseJsonBody(body);
    writeJson(response, 200, {
      id: "cmpl_mock",
      object: "text.completion",
      created: Math.floor(Date.now() / 1000),
      model: payload.model,
      prompt: [],
      choices: [{ text: "mock traces easy to inspect", finish_reason: "stop" }],
      usage: { prompt_tokens: 6, completion_tokens: 5, total_tokens: 11 },
    });
    return;
  }

  if (url.pathname === "/v1/embeddings") {
    const payload = parseJsonBody(body);
    writeJson(response, 200, {
      object: "list",
      model: payload.model,
      data: [{ object: "embedding", index: 0, embedding: [0.11, 0.22, 0.33, 0.44] }],
    });
    return;
  }

  if (url.pathname === "/v1/images/generations") {
    const payload = parseJsonBody(body);
    writeJson(response, 200, {
      id: "img_mock",
      object: "list",
      model: payload.model,
      data: [{ index: 0, type: "url", url: "https://example.com/respan-mock-image.png" }],
    });
    return;
  }

  if (url.pathname === "/v1/rerank") {
    const payload = parseJsonBody(body);
    writeJson(response, 200, {
      id: "rerank_mock",
      object: "rerank",
      model: payload.model,
      results: [
        { index: 0, relevance_score: 0.97, document: { text: "Respan captures traces and spans for model calls." } },
        { index: 1, relevance_score: 0.21, document: { text: "This document is about invoice processing." } },
      ],
      usage: { prompt_tokens: 10, completion_tokens: 0, total_tokens: 10 },
    });
    return;
  }

  if (url.pathname === "/v1/audio/speech") {
    response.writeHead(200, {
      "content-type": "application/octet-stream",
      "content-length": "12",
    });
    response.end(Buffer.from("mock-audio!!"));
    return;
  }

  if (url.pathname === "/v1/audio/transcriptions") {
    writeJson(response, 200, { text: "mock transcription" });
    return;
  }

  if (url.pathname === "/v1/audio/translations") {
    writeJson(response, 200, { text: "mock translation" });
    return;
  }

  writeJson(response, 404, { error: { message: `Unhandled mock path: ${url.pathname}` } });
}

async function readBody(request: IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString("utf8");
}

function parseJsonBody(body: string): Record<string, any> {
  if (!body.trim()) return {};
  try {
    return JSON.parse(body);
  } catch {
    return {};
  }
}

function writeJson(response: ServerResponse, statusCode: number, payload: unknown): void {
  const body = JSON.stringify(payload);
  response.writeHead(statusCode, {
    "content-type": "application/json",
    "content-length": Buffer.byteLength(body),
  });
  response.end(body);
}

function writeSse(response: ServerResponse, chunks: unknown[]): void {
  response.writeHead(200, {
    "content-type": "text/event-stream",
    "cache-control": "no-cache",
    connection: "keep-alive",
  });
  for (const chunk of chunks) {
    response.write(`data: ${JSON.stringify(chunk)}\n\n`);
  }
  response.end("data: [DONE]\n\n");
}
