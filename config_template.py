"""
Configuration template for AI Newspaper Agent.
Copy this file to config.py and ensure .env is populated, or load .env and use os.getenv directly.
Never commit config.py if it contains secrets. This template documents expected environment variables.
"""

import os
from pathlib import Path

# Base path (project root)
BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# API keys (required) - load from .env via python-dotenv before importing app
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ---------------------------------------------------------------------------
# Server (optional)
# ---------------------------------------------------------------------------
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# Paths for frontend assets
# ---------------------------------------------------------------------------
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
