import { MODEL, createRuntime, runCase } from "./_shared.js";

const caseId = "streaming";
const { client, respan } = createRuntime();

try {
  const output = await runCase(respan, caseId, async () => {
    const stream = await client.messages.create({
      model: MODEL,
      max_tokens: 80,
      stream: true,
      messages: [
        { role: "user", content: "Reply with exactly: Anthropic streaming tracing works." },
      ],
    });

    let text = "";
    for await (const event of stream) {
      if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
        text += event.delta.text;
      }
    }
    return text;
  });
  console.log(JSON.stringify({ caseId, output }));
} finally {
  await respan.shutdown();
}
