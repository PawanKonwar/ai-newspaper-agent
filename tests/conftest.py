"""
Pytest configuration and fixtures for AI Newspaper Agent.
Ensures project root is on sys.path and loads .env so tests see config.
"""

import os
import sys

import pytest
from dotenv import load_dotenv

# Project root on path so "app" and config resolve
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Load .env so app.config and pipeline see API keys when present
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
