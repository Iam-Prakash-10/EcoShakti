#!/bin/bash
# Minimal startup script for Render - No worker class dependencies

echo "🔧 Starting EcoShakti (Minimal Mode - No Worker Class)..."

# Set environment
export FLASK_ENV=production

# Get port from environment
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable not set!"
    exit 1
fi

echo "Using PORT: $PORT"

# Create basic directories
mkdir -p logs uploads

# Start with absolutely minimal gunicorn - no worker class
echo "Starting gunicorn server (sync worker) on 0.0.0.0:$PORT..."
exec gunicorn \
  --bind "0.0.0.0:$PORT" \
  --workers 1 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  app:app