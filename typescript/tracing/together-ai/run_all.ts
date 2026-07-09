import dotenv from "dotenv";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { startTogetherMockServer, type TogetherMockServer } from "./_mock_server.js";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(exampleDir, "../../..");
dotenv.config({ path: path.join(repoRoot, ".env") });

const scripts = [
  "01_chat_completion.ts",
  "02_chat_streaming.ts",
  "03_tool_calls.ts",
  "04_text_completion_embedding.ts",
  "05_image_rerank.ts",
  "06_audio_transcription_translation.ts",
  "07_expected_error.ts",
];

let mockServer: TogetherMockServer | undefined;
const childEnv: NodeJS.ProcessEnv = { ...process.env };
if (!childEnv.TOGETHER_API_KEY && childEnv.TOGETHER_EXAMPLE_DISABLE_MOCK !== "1") {
  mockServer = await startTogetherMockServer();
  childEnv.TOGETHER_API_KEY = "sk-respan-together-mock";
  childEnv.TOGETHER_BASE_URL = mockServer.baseURL;
  console.log(JSON.stringify({ togetherMockServer: true, baseURL: mockServer.baseURL }, null, 2));
}

const failures: string[] = [];
try {
  for (const script of scripts) {
    try {
      await runScript(script, childEnv);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      failures.push(`${script}: ${message}`);
    }
  }
} finally {
  await mockServer?.close();
}

if (failures.length > 0) {
  console.error(JSON.stringify({ failures }, null, 2));
  process.exitCode = 1;
}

function runScript(script: string, env: NodeJS.ProcessEnv): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(
      process.execPath,
      ["--import", "tsx", path.join(exampleDir, script)],
      {
        cwd: exampleDir,
        env,
        stdio: "inherit",
      },
    );
    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${script} exited with code ${code}`));
    });
  });
}
