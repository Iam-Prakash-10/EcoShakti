#!/usr/bin/env python3
"""
Minimal startup script for debugging port binding issues
"""
import os
import sys

def main():
    print("🔍 Debugging EcoShakti startup...")
    
    # Check environment variables
    port = os.environ.get('PORT')
    print(f"PORT environment variable: {port}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    if not port:
        print("❌ ERROR: PORT environment variable not set!")
        sys.exit(1)
    
    try:
        port_int = int(port)
        print(f"✅ PORT is valid integer: {port_int}")
    except ValueError:
        print(f"❌ ERROR: PORT is not a valid integer: {port}")
        sys.exit(1)
    
    # Try to import the app
    try:
        print("📦 Importing Flask app...")
        # Set production mode before import to avoid any eventlet issues
        os.environ['FLASK_ENV'] = 'production'
        from app import app
        print("✅ App imported successfully")
        
        # Test the health endpoint
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"✅ Health check: {response.status_code}")
        
        # Start with simple wsgi server for testing
        print(f"🚀 Starting app on 0.0.0.0:{port}...")
        app.run(host='0.0.0.0', port=port_int, debug=False)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()