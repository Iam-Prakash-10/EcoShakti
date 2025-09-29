#!/usr/bin/env python3
"""
Python-based startup script for EcoShakti on Render
This is a fallback if bash scripts don't work
"""
import os
import sys
import subprocess

def main():
    print("🚀 Starting EcoShakti with Python startup script...")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # Change to the correct directory
    try:
        os.chdir('/opt/render/project/src')
        print(f"Changed to directory: {os.getcwd()}")
    except:
        print(f"Using current directory: {os.getcwd()}")
    
    # Start gunicorn
    cmd = ['gunicorn', '--config', 'gunicorn.conf.py', 'app:app']
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        # Replace current process with gunicorn
        os.execvp('gunicorn', cmd)
    except Exception as e:
        print(f"Failed to start gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()