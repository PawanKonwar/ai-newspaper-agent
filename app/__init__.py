"""AI Newspaper Agent - Three-stage LLM pipeline for automated journalism."""

# Ensure project root is on sys.path so "app" submodules
# (app.config, app.pipeline) resolve regardless of how this
# package was loaded (e.g. editable install, PYTHONPATH, conftest).
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

__version__ = "1.0.0"
