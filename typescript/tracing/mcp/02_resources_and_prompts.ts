import {
  createDemoMcpEnvironment,
  createRespan,
  logExampleResult,
  runWithExampleTrace,
} from "./_shared.js";

const workflowName = "TypeScript MCP Resources And Prompts Example";

export async function resourcesAndPromptsExample(): Promise<void> {
  const respan = createRespan("typescript-mcp-resources-prompts-example");
  await respan.initialize();

  try {
    const result = await runWithExampleTrace(respan, workflowName, async () => {
      const env = await createDemoMcpEnvironment();
      try {
        const resources = await env.client.listResources();
        const templates = await env.client.listResourceTemplates();
        const contents = await env.client.readResource({ uri: "demo://city/paris" });
        const prompts = await env.client.listPrompts();
        const prompt = await env.client.getPrompt({
          name: "city_brief",
          arguments: { city: "Paris" },
        });
        return { resources, templates, contents, prompts, prompt };
      } finally {
        await env.close();
      }
    });

    logExampleResult(workflowName, {
      resources: result.resources.resources.map((resource) => resource.uri),
      templates: result.templates.resourceTemplates.map((template) => template.uriTemplate),
      promptNames: result.prompts.prompts.map((prompt) => prompt.name),
      firstPromptMessage: result.prompt.messages[0]?.content,
      firstResourceText: result.contents.contents[0] && "text" in result.contents.contents[0] ? result.contents.contents[0].text : undefined,
    });
  } finally {
  }
}

await resourcesAndPromptsExample();
