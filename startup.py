#!/usr/bin/env python3
"""
Startup script for production deployment
Ensures proper initialization before starting gunicorn
"""
import os
import sys

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create necessary directories
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

print("Production startup complete - ready for gunicorn")