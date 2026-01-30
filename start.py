#!/usr/bin/env python3
"""
Startup script for AI Newspaper Agent.
Checks .env and dependencies, then runs the app. Use: python start.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

REQUIRED_KEYS = ("OPENAI_API_KEY", "DEEPSEEK_API_KEY", "GOOGLE_API_KEY")


def check_env() -> tuple[bool, str]:
    """Verify .env exists and required API keys are set. Returns (ok, message)."""
    env_path = _PROJECT_ROOT / ".env"
    if not env_path.exists():
        return False, (
            "No .env file found. Copy .env.example to .env and add your API keys."
        )
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        return False, f"Missing in .env: {', '.join(missing)}"
    return True, "Environment configured"


def main() -> None:
    """Check environment, then start the uvicorn server."""
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))

    print("AI Newspaper Agent")
    print("=" * 50)

    ok, msg = check_env()
    if not ok:
        print(f"Error: {msg}")
        print("  cp .env.example .env")
        print("  Then edit .env with your API keys.")
        sys.exit(1)
    print(f"  {msg}")

    try:
        import uvicorn
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    print("  Starting server at http://localhost:8000")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    try:
        uvicorn.run(
            "app.main:app",
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", "8000")),
            reload=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
