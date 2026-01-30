"""
Pytest configuration and fixtures for AI Newspaper Agent.
Ensures project root is on sys.path so tests can import app.config,
app.pipeline, etc.
"""

import os
import sys

from dotenv import load_dotenv

# Resolve project root: conftest.py lives in tests/, so parent is project root.
# This makes "app" importable regardless of cwd.
# (e.g. when CI runs pytest from repo root).
_current_file = os.path.realpath(__file__)
_conftest_dir = os.path.dirname(_current_file)
_project_root = os.path.dirname(_conftest_dir)

if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Load .env so app.config and pipeline see API keys when present
_env_path = os.path.join(_project_root, ".env")
load_dotenv(_env_path)
