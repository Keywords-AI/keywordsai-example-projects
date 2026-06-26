import Together from "together-ai";
import fs from "node:fs/promises";
import {
  MODELS,
  captureFeature,
  createDemoWav,
  createRespan,
  createTogether,
  logExampleResult,
  runWithTogetherWorkflow,
  shutdownRespan,
} from "./_shared.js";

const workflowName = "together-ai-ts-audio-transcription-translation";
const respan = createRespan("together-ai-typescript-audio");

try {
  const details = await runWithTogetherWorkflow(respan, workflowName, async () => {
    const client = createTogether();
    const speech = await captureFeature("together speech", async () => {
      const response = await client.audio.speech.create({
        model: MODELS.speech,
        voice: MODELS.speechVoice,
        input: "Respan Together AI speech tracing succeeded.",
        response_format: "mp3",
      });
      const bytes = await response.arrayBuffer();
      return { model: MODELS.speech, bytes: bytes.byteLength };
    });

    const wavPath = await createDemoWav();
    const wavFile = await Together.toFile(await fs.readFile(wavPath), "respan-demo.wav");

    const transcription = await captureFeature("together transcription", async () => {
      const response = await client.audio.transcriptions.create({
        file: wavFile,
        model: MODELS.transcription as any,
        response_format: "json",
      });
      return { text: response.text ?? "" };
    });

    const translationFile = await Together.toFile(await fs.readFile(wavPath), "respan-demo.wav");
    const translation = await captureFeature("together translation", async () => {
      const response = await client.audio.translations.create({
        file: translationFile,
        model: MODELS.transcription as any,
        response_format: "json",
      });
      return { text: response.text ?? "" };
    });

    return { speech, transcription, translation };
  });

  logExampleResult(workflowName, details);
} finally {
  await shutdownRespan(respan);
}
