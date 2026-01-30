"""
Pytest configuration and fixtures for AI Newspaper Agent.
Ensures project root is on sys.path so tests can import app.config, app.pipeline, etc.
"""

import os
import sys

from dotenv import load_dotenv

# Add project root to sys.path so "app" package is findable (app.config, app.main, app.pipeline)
_conftest_dir = os.path.abspath(os.path.dirname(__file__))
_project_root = os.path.abspath(os.path.join(_conftest_dir, os.pardir))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Load .env so app.config and pipeline see API keys when present
load_dotenv(os.path.join(_project_root, ".env"))
