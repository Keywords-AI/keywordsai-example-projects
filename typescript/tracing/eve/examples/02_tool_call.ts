import { runToolCall } from "./_cases.js";
import { runWithEveServer } from "./_shared.js";

await runWithEveServer(async (client) => [await runToolCall(client)]);
