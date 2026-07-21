import dotenv from "dotenv";
import { fileURLToPath } from "node:url";

dotenv.config({
  path: fileURLToPath(new URL("../../../.env", import.meta.url)),
  override: false,
  quiet: true,
});

export const EXAMPLE_RUN_ID =
  process.env.RESPAN_EXAMPLE_RUN_ID ?? "eve-ts-" + Date.now();

export const RESPAN_API_KEY = requireEnvironment("RESPAN_API_KEY");

export const RESPAN_BASE_URL =
  process.env.RESPAN_BASE_URL ?? "https://api.respan.ai";

function requireEnvironment(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(
      name + " is required. Add it to respan-example-projects/.env.",
    );
  }
  return value;
}
