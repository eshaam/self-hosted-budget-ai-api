module.exports = {
  apps: [{
    name: 'budget-ai-api',
    script: 'venv/bin/python',
    args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
    cwd: '/home/deploy/self-hosted-budget-ai-api/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '4G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/home/deploy/self-hosted-budget-ai-api/backend'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
