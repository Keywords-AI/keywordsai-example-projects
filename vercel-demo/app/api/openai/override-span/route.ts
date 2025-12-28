import { createOpenAI, openai } from "@ai-sdk/openai";
import { generateText } from "ai";
import { trace } from "@opentelemetry/api";

export const maxDuration = 30;

export async function POST(req: Request) {
  const { message, id } = await req.json();
  const steps: any[] = [];

  console.log("chat id:", id || "no-id-provided");

  const keywordsaiApiKeyFromUI = req.headers.get("x-keywordsai-api-key")?.trim();
  if (keywordsaiApiKeyFromUI) {
    (globalThis as any).__KEYWORDSAI_RUNTIME_API_KEY__ = keywordsaiApiKeyFromUI;
  }

  const apiKeyFromUI = req.headers.get("x-openai-api-key")?.trim();
  const openaiProvider = apiKeyFromUI ? createOpenAI({ apiKey: apiKeyFromUI }) : openai;

  // Header creator for KeywordsAI system parameters (same as basic-workflow)
  const createHeader = () => {
    return {
      "X-Data-Keywordsai-Params": Buffer.from(
        JSON.stringify({
          customer_identifier: "user_demo_123",
          trace_group_identifier: "basic_handoff_group",
          prompt_unit_price: 100000,
        }),
      ).toString("base64"),
    };
  };

  // Step 1: Triage Agent (same as basic-workflow)
  const triageResult = await generateText({
    model: openaiProvider("gpt-4o-mini"),
    prompt: `Analyze the language of this message: "${message}". Return ONLY the language name.`,
    headers: createHeader(),
    experimental_telemetry: {
      isEnabled: true,
      functionId: "triage-agent",
      metadata: {
        agent: "Triage Agent",
        step: 1,
        environment: "demo",
        feature: "override-span",
      },
    },
  });

  const language = triageResult.text.trim();
  steps.push({
    agent: "Triage Agent",
    action: "Analyzing language...",
    output: `Detected Language: ${language}.`,
  });

  // Step 2: Specialist Agent (same as basic-workflow, BUT rename the main doGenerate span)
  const renamedSpans: Array<{ from: string; to: string }> = [];
  const baseTracer = trace.getTracer("ai");

  // Keep "doGenerate" in the name so KeywordsAI exporter dedup still works (no duplicate spans in UI).
  const renamedStep2SpanName = "Override Demo - Step 2 (Specialist) doGenerate";

  const renamingTracer = {
    ...baseTracer,
    startSpan(name: string, ...rest: any[]) {
      const span = (baseTracer as any).startSpan(name, ...rest);
      if (name === "ai.generateText.doGenerate" && span?.updateName) {
        renamedSpans.push({ from: name, to: renamedStep2SpanName });
        span.updateName(renamedStep2SpanName);
      }
      return span;
    },
    startActiveSpan(name: string, ...rest: any[]) {
      const last = rest[rest.length - 1];
      if (typeof last !== "function") {
        return (baseTracer as any).startActiveSpan(name, ...rest);
      }

      const fn = last;
      const forwarded = rest.slice(0, -1);

      return (baseTracer as any).startActiveSpan(
        name,
        ...forwarded,
        (span: any) => {
          if (name === "ai.generateText.doGenerate" && span?.updateName) {
            renamedSpans.push({ from: name, to: renamedStep2SpanName });
            span.updateName(renamedStep2SpanName);
          }
          return fn(span);
        },
      );
    },
  } as any;

  const specialistResult = await generateText({
    model: openaiProvider("gpt-4o-mini"),
    prompt: `You are a specialist in ${language}. Respond to this message in ${language}: "${message}"`,
    headers: createHeader(),
    experimental_telemetry: {
      isEnabled: true,
      functionId: "specialist-agent",
      tracer: renamingTracer,
      metadata: {
        agent: `${language} Specialist`,
        step: 2,
        custom_tag: "pro_user",
        feature: "override-span",
        span_rename: renamedStep2SpanName,
      },
    },
  });

  steps.push({
    agent: `${language} Specialist`,
    action: `Generating ${language} response...`,
    output: specialistResult.text,
  });

  return Response.json({
    steps,
    renamed_spans: renamedSpans,
    system_metadata: {
      prompt_unit_price: 100000,
      customer_id: "user_demo_123",
      group_id: "basic_handoff_group",
    },
    custom_metadata: { environment: "demo", custom_tag: "pro_user" },
  });
}
