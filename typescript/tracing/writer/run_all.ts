import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const exampleDir = path.dirname(fileURLToPath(import.meta.url));
const scripts = [
  "01_basic_chat.ts",
  "02_streaming_chat.ts",
  "03_structured_output.ts",
  "04_tool_calling.ts",
  "05_text_completion.ts",
  "06_expected_error.ts",
];

for (const script of scripts) {
  await runScript(script);
}

function runScript(script: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(
      process.execPath,
      ["--import", "tsx", path.join(exampleDir, script)],
      {
        cwd: exampleDir,
        env: process.env,
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
