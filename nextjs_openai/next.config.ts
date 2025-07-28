import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config, { isServer }) => {
    // Enable symlink resolution for webpack
    config.resolve.symlinks = true;
    return config;
  },
};

export default nextConfig;
