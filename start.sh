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
exec gunicorn --config gunicorn.conf.py app:app