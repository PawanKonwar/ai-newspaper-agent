"""
Root conftest: ensure project root is on sys.path before any test or app code runs.
This runs when pytest starts (before tests/conftest.py or any test module).
Makes "app" importable as a package so app.config, app.pipeline, etc. resolve.
"""
import os
import sys

_root = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
