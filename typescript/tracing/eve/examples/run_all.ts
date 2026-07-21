import {
  runBasicTurn,
  runSubagentLineage,
  runToolCall,
} from "./_cases.js";
import { runWithEveServer } from "./_shared.js";

await runWithEveServer(async (client) => [
  await runBasicTurn(client),
  await runToolCall(client),
  await runSubagentLineage(client),
]);
