"""
Application configuration loaded from environment variables.

All secrets and tunables come from .env; no hardcoded credentials.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_BASE = Path(__file__).resolve().parent.parent
load_dotenv(_BASE / ".env")

BASE_DIR: Path = _BASE

# API keys (required for full pipeline)
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

# Server
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Defaults for API request parsing
DEFAULT_MAX_LENGTH: int = 1000
MIN_WORD_COUNT: int = 50
MAX_WORD_COUNT: int = 5000

# Pipeline: LLM model names and endpoints (override via env if needed)
GEMINI_EDIT_MODEL: str = os.getenv("GEMINI_EDIT_MODEL", "gemini-2.0-flash")
GEMINI_FALLBACK_MODEL: str = os.getenv(
    "GEMINI_FALLBACK_MODEL", "gemini-1.5-flash-latest"
)
DEEPSEEK_BASE_URL: str = os.getenv(
    "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions"
)

# Frontend asset paths
STATIC_DIR: Path = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR: Path = BASE_DIR / "frontend" / "templates"
