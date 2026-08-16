import { MODEL, createRuntime, runCase } from "./_shared.js";

const caseId = "basic";
const { client, respan } = createRuntime();

try {
  const output = await runCase(respan, caseId, async () => {
    const message = await client.messages.create({
      model: MODEL,
      max_tokens: 80,
      messages: [
        { role: "user", content: "Reply with exactly: Anthropic basic tracing works." },
      ],
    });
    return message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join(" ");
  });
  console.log(JSON.stringify({ caseId, output }));
} finally {
  await respan.shutdown();
}
