import {
  createAzureClient,
  createRespan,
  installMockAzureOpenAIResponses,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript Azure OpenAI Streaming Tool Example";

type StreamedToolCall = {
  id?: string;
  name?: string;
  argumentsText: string;
};

function lookupCity(city: string): { city: string; note: string } {
  return {
    city,
    note: city + " has active waterfront neighborhoods and frequent ferry traffic.",
  };
}

function mergeToolCallDelta(
  toolCalls: Map<number, StreamedToolCall>,
  delta: any,
): void {
  for (const toolCall of delta?.tool_calls ?? []) {
    const index = toolCall.index ?? 0;
    const current = toolCalls.get(index) ?? { argumentsText: "" };
    if (toolCall.id) {
      current.id = toolCall.id;
    }
    if (toolCall.function?.name) {
      current.name = toolCall.function.name;
    }
    if (toolCall.function?.arguments) {
      current.argumentsText += toolCall.function.arguments;
    }
    toolCalls.set(index, current);
  }
}

function parseFirstToolArguments(toolCalls: Map<number, StreamedToolCall>): {
  toolName: string;
  args: { city: string };
} {
  const firstToolCall = [...toolCalls.values()][0];
  if (!firstToolCall) {
    throw new Error("Expected the mocked Azure OpenAI stream to emit a tool call.");
  }

  const parsed = JSON.parse(firstToolCall.argumentsText) as { city?: string };
  return {
    toolName: firstToolCall.name || "lookup_city",
    args: { city: parsed.city || "Seattle" },
  };
}

export async function streamingToolCallsExample(): Promise<void> {
  const restoreMocks = installMockAzureOpenAIResponses();
  const respan = createRespan("typescript-azure-openai-streaming-tool-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const client = createAzureClient("gpt-4o-mini");
      const stream = await client.chat.completions.create({
        model: "gpt-4o-mini",
        stream: true,
        messages: [
          { role: "user", content: "Use the lookup_city tool for Seattle." },
        ],
        tools: [
          {
            type: "function",
            function: {
              name: "lookup_city",
              description: "Lookup a short city note.",
              parameters: {
                type: "object",
                properties: {
                  city: { type: "string" },
                },
                required: ["city"],
              },
            },
          },
        ],
        extraAttributes: {
          "respan.metadata.azure_feature": "streaming_tool_calls",
        },
      } as any);

      const chunks: string[] = [];
      const toolCalls = new Map<number, StreamedToolCall>();
      for await (const chunk of stream as any) {
        const delta = chunk.choices[0]?.delta;
        if (delta?.content) {
          chunks.push(delta.content);
        }
        mergeToolCallDelta(toolCalls, delta);
      }

      const streamedText = chunks.join("");
      const { toolName, args } = parseFirstToolArguments(toolCalls);
      const toolResult = await respan.withTool(
        { name: toolName },
        async ({ city }: { city: string }) => lookupCity(city),
        args,
      );

      const finalResponse = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "user", content: "Use the lookup_city tool for Seattle." },
          {
            role: "assistant",
            content: streamedText,
            tool_calls: [
              {
                id: "call_city",
                type: "function",
                function: {
                  name: toolName,
                  arguments: JSON.stringify(args),
                },
              },
            ],
          },
          {
            role: "tool",
            tool_call_id: "call_city",
            content: JSON.stringify(toolResult),
          },
        ],
        extraAttributes: {
          "respan.metadata.azure_feature": "tool_final_answer",
        },
      } as any);

      return {
        streamedText,
        toolResult,
        finalAnswer: finalResponse.choices[0]?.message?.content,
      };
    });

    logExampleResult(workflowName, result);
  } finally {
    await respan.shutdown();
    restoreMocks();
  }
}

await streamingToolCallsExample();
