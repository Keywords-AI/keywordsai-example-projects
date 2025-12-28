"use client";

import { useState } from "react";

type Provider = "openai" | "google" | "anthropic";

type Feature =
  | "basic-workflow"
  | "tool-use"
  | "override-span";

interface FeatureConfig {
  id: Feature;
  name: string;
  description: string;
  defaultPrompt: string;
}

const features: FeatureConfig[] = [
  { 
    id: "basic-workflow", 
    name: "Basic Trace & Workflow", 
    description: "Quickstart + Metadata + Agent Handoff", 
    defaultPrompt: "¿Cómo se dice 'hello' en español?" 
  },
  { 
    id: "tool-use", 
    name: "Tool Use", 
    description: "Agent calling external tools", 
    defaultPrompt: "What is the weather in Tokyo?"
  },
  { 
    id: "override-span", 
    name: "Override Span", 
    description: "Customize trace names and data", 
    defaultPrompt: "Secret message: The password is 12345"
  },
];

const providers: Array<{ id: Provider; name: string; enabled: boolean }> = [
  { id: "openai", name: "OpenAI", enabled: true },
  { id: "google", name: "Google (coming soon)", enabled: false },
  { id: "anthropic", name: "Anthropic (coming soon)", enabled: false },
];

export default function Home() {
  const [provider, setProvider] = useState<Provider>("openai");
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [openaiApiKey, setOpenaiApiKey] = useState<string>("");
  const [keywordsaiApiKey, setKeywordsaiApiKey] = useState<string>("");

  const handleFeatureClick = async (feature: FeatureConfig) => {
    setSelectedFeature(feature.id);
    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch(`/api/${provider}/${feature.id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(provider === "openai" && openaiApiKey
            ? { "x-openai-api-key": openaiApiKey }
            : {}),
          ...(keywordsaiApiKey ? { "x-keywordsai-api-key": keywordsaiApiKey } : {}),
        },
        body: JSON.stringify({ message: feature.defaultPrompt }),
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: error instanceof Error ? error.message : "Unknown error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      <div className="container mx-auto px-6 py-12 max-w-5xl">
        <div className="mb-12 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 tracking-tight">KeywordsAI Tracing Demo</h1>
            <p className="text-gray-600 italic uppercase text-[10px] tracking-widest font-bold">
              Vercel AI SDK Integration Showcase
            </p>
            <p className="text-[11px] text-gray-600 mt-2">
              Recommended: run locally with env vars for the simplest & safest setup.{" "}
              <a
                className="text-black underline underline-offset-4"
                href="https://docs.keywordsai.co/integration/development-frameworks/tracing/vercel-tracing?utm_source=agentblocks"
                target="_blank"
                rel="noreferrer"
              >
                docs.keywordsai.co
              </a>
            </p>
          </div>

          {/* Provider selector */}
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-bold uppercase text-gray-400 tracking-widest font-mono">
              Provider
            </span>
            <select
              className="border border-gray-200 bg-white px-3 py-2 text-xs font-mono hover:border-black focus:outline-none"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value as Provider);
                setSelectedFeature(null);
                setResponse(null);
              }}
              disabled={loading}
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id} disabled={!p.enabled}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* API keys (optional; for deploys without server env secrets) */}
        <div className="mb-12 border border-gray-200 bg-gray-50 p-4">
          <div className="mb-4">
            <p className="text-[10px] font-bold uppercase text-gray-400 tracking-widest font-mono">
              API Keys (optional)
            </p>
            <p className="text-xs text-gray-600">
              Not persisted. If you set the env vars in <span className="font-bold">.env.local</span>, you don’t need
              these.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <p className="text-[10px] font-bold uppercase text-gray-400 tracking-widest font-mono mb-2">
                OpenAI (<span className="font-bold">OPENAI_API_KEY</span>)
              </p>
              <div className="flex gap-2">
                <input
                  className="flex-1 border border-gray-200 bg-white px-3 py-2 text-xs font-mono hover:border-black focus:outline-none disabled:opacity-50"
                  type="password"
                  placeholder="sk-... (optional)"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  autoComplete="off"
                  disabled={loading || provider !== "openai"}
                />
                <button
                  className="border border-gray-200 bg-white px-3 py-2 text-xs font-mono hover:border-black disabled:opacity-50"
                  disabled={loading || provider !== "openai"}
                  onClick={() => setOpenaiApiKey("")}
                >
                  Clear
                </button>
              </div>
              {provider !== "openai" && (
                <p className="text-[11px] text-gray-600 mt-2">Switch provider to OpenAI to use this key.</p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase text-gray-400 tracking-widest font-mono mb-2">
                KeywordsAI (<span className="font-bold">KEYWORDSAI_API_KEY</span>)
              </p>
              <div className="flex gap-2">
                <input
                  className="flex-1 border border-gray-200 bg-white px-3 py-2 text-xs font-mono hover:border-black focus:outline-none disabled:opacity-50"
                  type="password"
                  placeholder="kwai_... (optional)"
                  value={keywordsaiApiKey}
                  onChange={(e) => setKeywordsaiApiKey(e.target.value)}
                  autoComplete="off"
                  disabled={loading}
                />
                <button
                  className="border border-gray-200 bg-white px-3 py-2 text-xs font-mono hover:border-black disabled:opacity-50"
                  disabled={loading}
                  onClick={() => setKeywordsaiApiKey("")}
                >
                  Clear
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          {features.map((feature) => (
            <button
              key={feature.id}
              onClick={() => handleFeatureClick(feature)}
              disabled={loading || providers.find((p) => p.id === provider)?.enabled === false}
              className={`text-left p-6 border transition-all ${
                selectedFeature === feature.id
                  ? "border-black bg-black text-white"
                  : "border-gray-200 hover:border-black"
              }`}
            >
              <h3 className="font-bold text-sm mb-2">{feature.name}</h3>
              <p className={`text-[11px] leading-relaxed ${selectedFeature === feature.id ? "text-gray-400" : "text-gray-500"}`}>
                {feature.description}
              </p>
            </button>
          ))}
        </div>

        {providers.find((p) => p.id === provider)?.enabled === false && (
          <div className="mb-12 border border-gray-200 bg-gray-50 p-4">
            <p className="text-xs font-mono text-gray-700">
              Provider not enabled yet. Switch to <span className="font-bold">OpenAI</span> for now.
            </p>
          </div>
        )}

        {/* Execution Result */}
        {selectedFeature && (
          <div className="border border-black p-8 bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,0.05)]">
            <div className="flex justify-between items-center mb-8 border-b border-gray-100 pb-4">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider">{selectedFeature.replace('-', ' ')} Result</h3>
              </div>
              {loading && <span className="text-xs animate-pulse font-bold tracking-tighter">● PROCESSING</span>}
            </div>

            {/* Prompt Display */}
            <div className="mb-8">
              <p className="text-[10px] font-bold uppercase text-gray-400 mb-2 tracking-widest font-mono">Example Input</p>
              <div className="p-4 bg-gray-50 border border-gray-100 font-mono text-xs text-gray-600">
                "{features.find(f => f.id === selectedFeature)?.defaultPrompt}"
              </div>
            </div>

            {/* Metadata Section (Combined View) */}
            {(response?.system_metadata || response?.custom_metadata) && (
              <div className="mb-8 p-4 bg-gray-50 border border-gray-100">
                <p className="text-[10px] font-bold uppercase text-gray-400 mb-3 tracking-widest font-mono">Metadata & Params Sent</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {response.system_metadata && (
                    <div>
                      <p className="text-[9px] font-bold text-gray-400 uppercase mb-1">KeywordsAI System IDs</p>
                      <pre className="text-[10px] font-mono text-black">
                        {JSON.stringify(response.system_metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                  {response.custom_metadata && (
                    <div>
                      <p className="text-[9px] font-bold text-gray-400 uppercase mb-1">Custom Analytics Data</p>
                      <pre className="text-[10px] font-mono text-black">
                        {JSON.stringify(response.custom_metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Response Section */}
            <div>
              <p className="text-[10px] font-bold uppercase text-gray-400 mb-2 tracking-widest font-mono">Execution Data</p>
              
              {response?.steps ? (
                <div className="space-y-6">
                  {response.steps.map((step: any, idx: number) => (
                    <div key={idx} className="border-l-2 border-black pl-6 py-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-[10px] font-bold bg-black text-white px-2 py-0.5">STEP {idx + 1}</span>
                        <span className="text-[10px] font-bold uppercase text-gray-400 tracking-tighter italic">{step.agent || "Action"}</span>
                      </div>
                      <p className="text-xs font-bold text-black mb-2">{step.action}</p>
                      <pre className="text-xs font-mono bg-gray-50 p-4 border border-gray-100 overflow-auto whitespace-pre-wrap leading-relaxed">
                        {step.output}
                      </pre>
                    </div>
                  ))}
                </div>
              ) : (
                <pre className="text-xs font-mono overflow-auto max-h-[400px] whitespace-pre-wrap bg-gray-50 p-4 border border-gray-100 leading-relaxed text-gray-700">
                  {response ? JSON.stringify(response, null, 2) : "Loading example..."}
                </pre>
              )}
            </div>

            {!loading && response && (
              <div className="mt-10 pt-6 border-t border-gray-100">
                <p className="text-[10px] uppercase font-bold tracking-[0.2em] text-gray-400 text-center">
                  Trace successfully ingested by Keywords AI
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
