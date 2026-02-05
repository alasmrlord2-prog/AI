// Jest setup file
import '@testing-library/jest-dom';

// Mock environment variables
process.env.NEXT_PUBLIC_AGENT_API_URL = 'http://localhost:8000';
process.env.NEXT_PUBLIC_BACKEND_URL = 'http://localhost:8000';
process.env.NEXT_PUBLIC_AGENT_WS_URL = 'ws://localhost:8000';

