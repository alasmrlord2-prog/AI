import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow cross-origin requests in development
  allowedDevOrigins: [
    "ai-agent.bankid-sy.com",
    "https://ai-agent.bankid-sy.com",
    "aaa.bankid-sy.com",
    "https://aaa.bankid-sy.com",
    "crm.bankid-sy.com",
    "https://crm.bankid-sy.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "3.76.209.35",
  ],
  // Enable standalone output for Docker
  output: 'standalone',
  // Rewrite API requests to backend
  async rewrites() {
    // Server-side: Use BACKEND_URL (Docker service name) or fallback
    // Client-side will use NEXT_PUBLIC_BACKEND_URL from getApiUrl()
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

