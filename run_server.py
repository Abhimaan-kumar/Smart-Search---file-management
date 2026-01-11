#!/usr/bin/env python3
"""
Quick start script for the Personal Smart Search & Organizer System
"""

import uvicorn
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

if __name__ == "__main__":
    print("=" * 60)
    print("Personal Smart Search & Organizer System")
    print("=" * 60)
    print("\nStarting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
