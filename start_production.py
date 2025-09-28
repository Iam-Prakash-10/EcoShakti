#!/usr/bin/env python3
"""
Production startup script for EcoShakti
"""
import os
from app import app

if __name__ == '__main__':
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Run with Socket.IO support
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        allow_unsafe_werkzeug=True  # For Socket.IO compatibility
    )