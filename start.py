#!/usr/bin/env python3
"""
AI Newspaper Agent - Startup Script
Convenient script to start the application with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import fastapi
        import uvicorn
        import langchain
        from langchain_google_genai import ChatGoogleGenerativeAI
        return True
    except ImportError:
        return False

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    if not env_file.exists():
        return False, "No .env file found"
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GOOGLE_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        return False, f"Missing API keys: {', '.join(missing_keys)}"
    
    return True, "All API keys configured"

def main():
    """Main startup function."""
    print("🚀 AI Newspaper Agent - Starting Application")
    print("=" * 50)
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        print("❌ Missing dependencies. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run manually:")
            print("pip install -r requirements.txt")
            return
    else:
        print("✅ All dependencies are installed")
    
    # Check environment configuration
    print("\n🔍 Checking environment configuration...")
    env_ok, env_message = check_env_file()
    if not env_ok:
        print(f"❌ {env_message}")
        print("\n📝 Please create a .env file with your API keys:")
        print("1. Copy env_example.txt to .env")
        print("2. Add your API keys to the .env file")
        print("3. Run this script again")
        return
    else:
        print(f"✅ {env_message}")
    
    # Start the application
    print("\n🚀 Starting the application...")
    print("📱 Open your browser and navigate to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the main application
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
