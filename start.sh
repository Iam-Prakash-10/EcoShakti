#!/bin/bash
# Render startup script for EcoShakti

echo "🚀 Starting EcoShakti application..."

# Ensure we're in the right directory
cd /opt/render/project/src

# Set production environment
export FLASK_ENV=production

# Create necessary directories
mkdir -p logs uploads

# Start the application with gunicorn
echo "Starting gunicorn server..."
echo "Binding to 0.0.0.0:${PORT:-5000}"
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --worker-class gevent --timeout 30 --preload app:app