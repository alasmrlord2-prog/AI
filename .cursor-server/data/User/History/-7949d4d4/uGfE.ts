import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow cross-origin requests in development
  allowedDevOrigins: [
    "ai-agent.bankid-sy.com",
    "https://ai-agent.bankid-sy.com",
    "http://localhost:3000",
    "3.76.209.35",
  ],
  // Enable standalone output for Docker
  output: 'standalone',
};

export default nextConfig;

