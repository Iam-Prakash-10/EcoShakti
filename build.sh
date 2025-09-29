#!/bin/bash
# Render deployment build script

echo "Starting EcoShakti build process..."

# Create necessary directories
mkdir -p logs uploads

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production

echo "Build completed successfully!"