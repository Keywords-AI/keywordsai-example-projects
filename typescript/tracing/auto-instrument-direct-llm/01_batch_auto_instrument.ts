import { Respan, type InstrumentationStatusEntry } from "@respan/respan";
import { loadAutoInstrumentExampleEnv, type AutoInstrumentExampleEnv } from "./_env.js";

const EXAMPLE_SET = "typescript/tracing/auto-instrument-direct-llm";
const BATCH_WORKFLOW_PREFIX = "ts_auto_instrument_batch";

type CaseState = "passed" | "skipped" | "failed";

interface CaseResult {
  sdk: string;
  state: CaseState;
  detail: string;
}

function runId(): string {
  return process.env.RESPAN_EXAMPLE_RUN_ID || `ts-auto-direct-llm-batch-${Date.now()}`;
}

function compact(value: string, max = 96): string {
  return value.length > max ? `${value.slice(0, max - 1)}...` : value;
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return JSON.stringify(error);
}

function printInstrumentationStatus(status: InstrumentationStatusEntry[]): void {
  const rows = status.map((entry) => ({
    id: entry.id,
    category: entry.category,
    status: entry.status,
    package: entry.instrumentationPackage,
    reason: entry.reason ?? "",
  }));
  console.log("Auto-instrumentation registry status:");
  console.table(rows);
}

function printSupportedDirectLlms(status: InstrumentationStatusEntry[]): void {
  const rows = status
    .filter((entry) => entry.category === "direct-llm")
    .map((entry) => ({
      sdk: entry.id,
      sdkPackage: entry.sdkPackage,
      autoStatus: entry.status,
    }));
  console.log("Supported direct LLM SDK auto-instrumentations:");
  console.table(rows);
}

async function withSdkWorkflow<T>(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
  sdk: string,
  fn: () => Promise<T>,
): Promise<T> {
  const workflowName = `${BATCH_WORKFLOW_PREFIX}_${sdk.replace(/-/g, "_")}`;
  return await respan.propagateAttributes(
    {
      trace_group_identifier: currentRunId,
      metadata: {
        example_set: EXAMPLE_SET,
        run_id: currentRunId,
        sdk,
        gateway_base_url: env.gatewayBaseURL,
        auto_instrument: "direct-llm-batch",
      },
    },
    () =>
      respan.withWorkflow(
        {
          name: workflowName,
          associationProperties: {
            example_set: EXAMPLE_SET,
            language: "typescript",
            sdk,
            run_id: currentRunId,
          },
        },
        fn,
      ),
  );
}

async function runOpenAIGateway(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  try {
    const { default: OpenAI } = await import("openai");
    const openai = new OpenAI({
      apiKey: env.gatewayApiKey,
      baseURL: env.gatewayBaseURL,
    });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "openai", async () => {
      const completion = await openai.chat.completions.create({
        model: env.model,
        messages: [
          { role: "system", content: "You are a concise tracing test assistant." },
          { role: "user", content: "Reply with one short sentence that includes OpenAI auto instrumentation." },
        ],
      });
      return completion.choices[0]?.message?.content ?? "";
    });

    return { sdk: "openai", state: "passed", detail: compact(answer) };
  } catch (error) {
    return { sdk: "openai", state: "failed", detail: errorMessage(error) };
  }
}

async function runAnthropicGateway(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  try {
    const { default: Anthropic } = await import("@anthropic-ai/sdk");
    const anthropic = new Anthropic({
      apiKey: env.gatewayApiKey,
      baseURL: `${env.gatewayBaseURL}/anthropic`,
    });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "anthropic", async () => {
      const message = await anthropic.messages.create({
        model: env.anthropicModel,
        max_tokens: 80,
        messages: [
          {
            role: "user",
            content: "Reply with one short sentence that includes Anthropic auto instrumentation.",
          },
        ],
      });
      return message.content
        .map((block: any) => (block?.type === "text" ? block.text : ""))
        .filter(Boolean)
        .join(" ");
    });

    return { sdk: "anthropic", state: "passed", detail: compact(answer) };
  } catch (error) {
    return { sdk: "anthropic", state: "failed", detail: errorMessage(error) };
  }
}

async function runAzureOpenAI(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  try {
    const openaiModule = await import("openai");
    const OpenAI = (openaiModule.default ?? openaiModule.OpenAI) as any;
    const AzureOpenAI = openaiModule.AzureOpenAI as any;

    class RespanGatewayAzureOpenAI extends AzureOpenAI {
      constructor(options: any) {
        super(options);
      }

      buildRequest(options: any, props?: any) {
        return OpenAI.prototype.buildRequest.call(this, options, props);
      }
    }

    const client = new RespanGatewayAzureOpenAI({
      apiKey: env.gatewayApiKey,
      baseURL: env.gatewayBaseURL,
      apiVersion: "2024-10-21",
      defaultHeaders: { Authorization: `Bearer ${env.gatewayApiKey}` },
    });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "azure-openai", async () => {
      const completion = await client.chat.completions.create({
        model: env.azureGatewayModel,
        messages: [
          { role: "user", content: "Reply with one short sentence that includes Azure OpenAI auto instrumentation." },
        ],
      });
      return completion.choices[0]?.message?.content ?? "";
    });

    return {
      sdk: "azure-openai",
      state: "passed",
      detail: `${env.azureGatewayModel}: ${compact(answer || "(empty response)")}`,
    };
  } catch (error) {
    return { sdk: "azure-openai", state: "failed", detail: errorMessage(error) };
  }
}

async function runVertexAI(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  if (!env.vertexAI) {
    return {
      sdk: "vertexai",
      state: "skipped",
      detail: "set GOOGLE_CLOUD_PROJECT/VERTEXAI_PROJECT and GOOGLE_CLOUD_LOCATION/VERTEXAI_LOCATION",
    };
  }

  try {
    const { VertexAI } = await import("@google-cloud/vertexai");
    const vertexAI = new VertexAI({
      project: env.vertexAI.project,
      location: env.vertexAI.location,
    });
    const model = vertexAI.getGenerativeModel({ model: env.vertexAI.model });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "vertexai", async () => {
      const result = await model.generateContent("Reply with one short sentence that includes Vertex AI auto instrumentation.");
      return result.response.candidates?.[0]?.content?.parts?.map((part: any) => part.text ?? "").join(" ") ?? "";
    });

    return { sdk: "vertexai", state: "passed", detail: compact(answer) };
  } catch (error) {
    return { sdk: "vertexai", state: "failed", detail: errorMessage(error) };
  }
}

async function runVertexAIGatewayOpenAICompatible(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  if (!env.vertexGatewayModel) {
    return {
      sdk: "vertexai-gateway-openai-compatible",
      state: "skipped",
      detail: "set RESPAN_VERTEX_GATEWAY_MODEL to test a Vertex provider slug through the OpenAI-compatible gateway",
    };
  }

  try {
    const { default: OpenAI } = await import("openai");
    const openai = new OpenAI({
      apiKey: env.gatewayApiKey,
      baseURL: env.gatewayBaseURL,
    });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "vertexai-gateway", async () => {
      const completion = await openai.chat.completions.create({
        model: env.vertexGatewayModel!,
        messages: [
          { role: "user", content: "Reply with one short sentence that includes Vertex AI gateway routing." },
        ],
      });
      return completion.choices[0]?.message?.content ?? "";
    });

    return {
      sdk: "vertexai-gateway-openai-compatible",
      state: "passed",
      detail: `${env.vertexGatewayModel}: ${compact(answer || "(empty response)")}`,
    };
  } catch (error) {
    return { sdk: "vertexai-gateway-openai-compatible", state: "failed", detail: errorMessage(error) };
  }
}

async function runOpenRouter(
  respan: Respan,
  env: AutoInstrumentExampleEnv,
  currentRunId: string,
): Promise<CaseResult> {
  try {
    const chatModule = (await import("@openrouter/sdk/sdk/chat.js")) as any;
    const Chat = chatModule.Chat;
    const chat = new Chat({
      apiKey: env.gatewayApiKey,
      serverURL: env.gatewayBaseURL,
      appTitle: "Respan auto-instrument batch example",
    });

    const answer = await withSdkWorkflow(respan, env, currentRunId, "openrouter", async () => {
      const result = await chat.send({
        chatRequest: {
          model: env.openRouterGatewayModel,
          messages: [
            { role: "user", content: "Reply with one short sentence that includes OpenRouter auto instrumentation." },
          ],
        },
      });
      const choice = result?.choices?.[0];
      return choice?.message?.content ?? choice?.text ?? JSON.stringify(result);
    });

    return {
      sdk: "openrouter",
      state: "passed",
      detail: `${env.openRouterGatewayModel}: ${compact(answer || "(empty response)")}`,
    };
  } catch (error) {
    return { sdk: "openrouter", state: "failed", detail: errorMessage(error) };
  }
}

async function main(): Promise<void> {
  const env = loadAutoInstrumentExampleEnv();
  const currentRunId = runId();

  const respan = new Respan({
    apiKey: env.respanApiKey,
    baseURL: env.respanBaseURL,
    appName: "respan-ts-auto-instrument-direct-llm-batch-example",
    logLevel: "error",
    silenceInitializationMessage: true,
  });

  await respan.initialize();
  const status = respan.getInstrumentationStatus();
  printInstrumentationStatus(status);
  printSupportedDirectLlms(status);

  try {
    const results: CaseResult[] = [];
    results.push(await runOpenAIGateway(respan, env, currentRunId));
    results.push(await runAnthropicGateway(respan, env, currentRunId));
    results.push(await runAzureOpenAI(respan, env, currentRunId));
    results.push(await runVertexAI(respan, env, currentRunId));
    results.push(await runVertexAIGatewayOpenAICompatible(respan, env, currentRunId));
    results.push(await runOpenRouter(respan, env, currentRunId));

    console.log(`batch_run_id: ${currentRunId}`);
    console.log("Batch run summary:");
    console.table(results);

    if (!results.some((result) => result.state === "passed")) {
      process.exitCode = 1;
    }
  } finally {
    await respan.shutdown();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
