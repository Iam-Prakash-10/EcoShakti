#!/bin/bash
# Ultra-simple startup script for Render

echo "🚀 Starting EcoShakti (Ultra-Simple Mode)..."

# Set environment
export FLASK_ENV=production

# Get port from environment (Render provides this)
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable not set!"
    exit 1
fi

echo "Using PORT: $PORT"

# Create basic directories (no heavy operations)
mkdir -p logs uploads

# Start with minimal gunicorn configuration
echo "Starting gunicorn server on 0.0.0.0:$PORT..."
exec gunicorn \
  --bind "0.0.0.0:$PORT" \
  --workers 1 \
  --worker-class gevent \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  app:app