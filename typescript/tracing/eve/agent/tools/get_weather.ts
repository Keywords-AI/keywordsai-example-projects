import { defineTool } from "eve/tools";
import { never } from "eve/tools/approval";
import { z } from "zod";

export default defineTool({
  approval: never(),
  description: "Return deterministic weather for the requested city.",
  inputSchema: z.object({
    city: z.string().min(1),
  }),
  async execute({ city }) {
    return {
      city,
      condition: "Sunny",
      temperatureC: 24,
    };
  },
});
