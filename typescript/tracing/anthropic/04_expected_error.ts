import { createRuntime, runCase } from "./_shared.js";

const caseId = "failure";
const { client, respan } = createRuntime();

try {
  const output = await runCase(respan, caseId, async () => {
    try {
      await client.messages.create({
        model: "respan-intentional-anthropic-error-model",
        max_tokens: 20,
        messages: [
          { role: "user", content: "Exercise the expected Anthropic failure path." },
        ],
      });
      throw new Error("Expected the unsupported Anthropic model request to fail.");
    } catch (error) {
      if (error instanceof Error && error.message.startsWith("Expected the unsupported")) {
        throw error;
      }
      return {
        status:
          typeof error === "object" && error !== null && "status" in error
            ? error.status
            : undefined,
        message: error instanceof Error ? error.message.slice(0, 240) : String(error).slice(0, 240),
      };
    }
  });
  console.log(JSON.stringify({ caseId, expectedFailure: output }));
} finally {
  await respan.shutdown();
}
