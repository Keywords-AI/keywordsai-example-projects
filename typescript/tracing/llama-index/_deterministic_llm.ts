import { MockLLM } from "@llamaindex/core/llms/mock";
import { randomUUID } from "node:crypto";
import { Settings } from "llamaindex";

type MockLlmOptions = ConstructorParameters<typeof MockLLM>[0];

export class TracedMockLLM extends MockLLM {
  constructor(options: MockLlmOptions = {}) {
    super({
      timeBetweenToken: 0,
      metadata: {
        model: "respan-deterministic-llamaindex",
        temperature: 0,
        topP: 1,
        contextWindow: 8_192,
        tokenizer: undefined,
        structuredOutput: true,
      },
      ...options,
    });
  }

  get model(): string {
    return this.metadata.model;
  }

  async chat(params: any): Promise<any> {
    const id = randomUUID();
    Settings.callbackManager.dispatchEvent(
      "llm-start",
      { id, messages: params.messages },
      true,
    );
    const response = await super.chat(params);
    if (response && typeof response === "object" && Symbol.asyncIterator in response) {
      const originalIterator = response[Symbol.asyncIterator].bind(response);
      const model = this.model;
      return {
        async *[Symbol.asyncIterator]() {
          let content = "";
          const iterator = originalIterator();
          while (true) {
            const next = await iterator.next();
            if (next.done) break;
            const chunk = next.value;
            content += String(chunk.delta ?? "");
            yield chunk;
          }
          Settings.callbackManager.dispatchEvent(
            "llm-end",
            {
              id,
              response: tracedResponse(model, {
                message: { role: "assistant", content },
                raw: {},
              }),
            },
            true,
          );
        },
      };
    }

    const traced = tracedResponse(this.model, response);
    Settings.callbackManager.dispatchEvent(
      "llm-end",
      { id, response: traced },
      true,
    );
    return traced;
  }

  async complete(params: any): Promise<any> {
    if (params.stream) {
      throw new Error("The deterministic example LLM does not use completion streaming.");
    }
    const response = await this.chat({
      messages: [{ role: "user", content: params.prompt }],
      stream: false,
    });
    return {
      text: String(response.message.content ?? ""),
      raw: response.raw,
    };
  }
}

function tracedResponse(model: string, response: any): any {
  return {
    ...response,
    raw: {
      ...(response?.raw && typeof response.raw === "object" ? response.raw : {}),
      model,
      usage: {
        prompt_tokens: 12,
        completion_tokens: 8,
        total_tokens: 20,
      },
    },
  };
}
