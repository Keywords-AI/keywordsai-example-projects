import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  experimental: {
    instrumentationHook: true,
  },
  serverExternalPackages: ["ai", "@ai-sdk/openai", "@vercel/otel", "@opentelemetry/api"],
};

export default nextConfig;
