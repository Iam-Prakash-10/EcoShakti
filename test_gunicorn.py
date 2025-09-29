#!/usr/bin/env python3
"""
Test script to verify gunicorn setup
"""
import subprocess
import sys
import os

def test_gunicorn_config():
    """Test if gunicorn can load the app with our configuration"""
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        # Test gunicorn configuration
        print("Testing gunicorn configuration...")
        result = subprocess.run([
            'gunicorn', 
            '--config', 'gunicorn.conf.py', 
            '--check-config',
            'app:app'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Gunicorn configuration is valid!")
            return True
        else:
            print("❌ Gunicorn configuration failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Gunicorn test timed out")
        return False
    except FileNotFoundError:
        print("❌ Gunicorn not found. Make sure it's installed:")
        print("pip install gunicorn eventlet")
        return False
    except Exception as e:
        print(f"❌ Error testing gunicorn: {e}")
        return False

if __name__ == '__main__':
    test_gunicorn_config()