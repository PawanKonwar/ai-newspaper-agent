#!/usr/bin/env python3
"""
Entry point for AI Newspaper Agent.
Loads .env from project root, then runs the FastAPI app with uvicorn.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root so API keys are found regardless of cwd
_PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(_PROJECT_ROOT / ".env")

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from app.main import run
    run()
