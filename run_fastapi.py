#!/usr/bin/env python3
"""
Script to install dependencies and run the FastAPI server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing FastAPI dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    
    try:
        # Run the FastAPI server
        subprocess.run([
            sys.executable, "fastapi_server.py"
        ])
    except KeyboardInterrupt:
        print("\n⚠️ Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    print("🔧 FastAPI Server Setup")
    print("=" * 30)
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies already installed")
    except ImportError:
        if not install_dependencies():
            sys.exit(1)
    
    # Run the server
    run_server() 