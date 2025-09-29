#!/bin/bash
# Ultra-simple startup script for Render - No eventlet dependency

echo "🚀 Starting EcoShakti (Clean Mode)..."

# Set environment
export FLASK_ENV=production

# Get port from environment (Render provides this)
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable not set!"
    exit 1
fi

echo "Using PORT: $PORT"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"

# Create basic directories (no heavy operations)
mkdir -p logs uploads

# List Python packages to verify gevent is installed
echo "Checking gevent installation..."
python -c "import gevent; print(f'gevent version: {gevent.__version__}')" || echo "gevent not found!"

# Start with clean gunicorn configuration - no eventlet
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