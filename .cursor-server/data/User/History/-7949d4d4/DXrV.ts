import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow cross-origin requests in development
  allowedDevOrigins: [
    "18.184.134.108",
    "http://18.184.134.108:3000",
    "http://localhost:3000",
  ],
};

export default nextConfig;

