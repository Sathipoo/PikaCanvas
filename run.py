#!/usr/bin/env python3
"""
PikaCanvas - Multi-Model AI Image Generation Platform
Main application entry point
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("🎨 Starting PikaCanvas...")
    print(f"🌐 Running on http://{host}:{port}")
    print("📱 Demo accounts:")
    print("   👤 admin / admin123")
    print("   👤 demo / demo123")
    
    app.run(host=host, port=port, debug=debug)