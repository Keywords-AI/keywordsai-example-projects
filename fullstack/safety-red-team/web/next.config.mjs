/** @type {import('next').NextConfig} */
const nextConfig = {
  // This example lives inside a multi-project repo; pin file tracing to this
  // app so Next doesn't infer a parent lockfile as the workspace root.
  outputFileTracingRoot: import.meta.dirname,
};

export default nextConfig;
