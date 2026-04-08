#!/usr/bin/env python3
"""
Production WSGI server startup script for Website Monitor.
Runs under waitress for multi-threaded concurrent request handling.

Usage:
    python run.py              # Start on 0.0.0.0:5000 (production)
    PRODUCTION=false python run.py  # Start in dev mode
"""

import os
import sys

# Set production mode
os.environ["FLASK_ENV"] = "production"
os.environ["PRODUCTION"] = "true"

try:
    from waitress import serve
    from app import app
    
    print("=" * 60)
    print("🚀 Website Monitor - Production WSGI Server")
    print("=" * 60)
    print("Listening on: http://0.0.0.0:5000")
    print("Threads: 4")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    serve(app, host="0.0.0.0", port=5000, threads=4)
except ImportError:
    print("[ERROR] waitress is not installed!")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n[INFO] Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Failed to start server: {e}")
    sys.exit(1)
