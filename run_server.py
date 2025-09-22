#!/usr/bin/env python3
"""
Tamil AI Assistant Server Launcher
Run this script to start the development server
"""

import uvicorn
import sys
import os

def main():
    """Launch the FastAPI server"""
    print("🚀 Starting Tamil AI Assistant Backend Server...")
    print("📱 Frontend will be accessible after starting the server")
    print("🌐 API Documentation will be available at: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload during development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()