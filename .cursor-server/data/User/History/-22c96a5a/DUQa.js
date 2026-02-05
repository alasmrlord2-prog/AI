// PM2 Ecosystem Configuration for all three frontends
module.exports = {
  apps: [
    {
      name: 'ai-agent-frontend',
      script: 'npm',
      args: 'run dev -- -p 3000',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000',
        NODE_ENV: 'development'
      },
      error_file: '/home/ai/ai-agent/frontend/logs/pm2-ai-agent-error.log',
      out_file: '/home/ai/ai-agent/frontend/logs/pm2-ai-agent-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'crm-frontend',
      script: 'npm',
      args: 'run dev -- -p 3001',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3001,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000',
        NODE_ENV: 'development'
      },
      error_file: '/tmp/pm2-crm-error.log',
      out_file: '/tmp/pm2-crm-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'aaa-frontend',
      script: 'npm',
      args: 'run dev -- -p 3002',
      cwd: '/home/ai/ai-agent/frontend',
      env: {
        PORT: 3002,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000',
        NODE_ENV: 'development'
      },
      error_file: '/tmp/pm2-aaa-error.log',
      out_file: '/tmp/pm2-aaa-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    }
  ]
};

