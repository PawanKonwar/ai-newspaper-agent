"""
Tests for AI Newspaper Agent application.
Run from project root: python -m pytest tests/ -v
"""

import asyncio
import os
import sys

import pytest
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Verify required packages are installed."""
    import fastapi
    import uvicorn
    import langchain
    from langchain_google_genai import ChatGoogleGenerativeAI
    assert fastapi
    assert uvicorn
    assert langchain
    assert ChatGoogleGenerativeAI


def test_env_keys_optional():
    """Env keys can be missing (stages will report unavailable)."""
    from app.pipeline import NewspaperPipeline
    pipeline = NewspaperPipeline()
    assert hasattr(pipeline, "research_stage")
    assert hasattr(pipeline, "draft_stage")
    assert hasattr(pipeline, "edit_stage")
    assert hasattr(pipeline, "run_pipeline")


@pytest.mark.asyncio
async def test_pipeline_structure():
    """Pipeline returns expected keys."""
    from app.pipeline import NewspaperPipeline
    pipeline = NewspaperPipeline()
    result = await pipeline.run_pipeline(topic="Test topic", max_length=500)
    assert "research_stage" in result
    assert "draft_stage" in result
    assert "final_stage" in result
    assert result["research_stage"]["status"] in ("success", "error", "skipped")
    assert result["draft_stage"]["status"] in ("success", "error", "skipped")
    assert result["final_stage"]["status"] in ("success", "error", "skipped")


def test_fastapi_app():
    """FastAPI app can be imported and has routes."""
    from app.main import app
    routes = [r.path for r in app.routes]
    assert "/" in routes
    assert "/health" in routes
