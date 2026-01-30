"""
Tests for AI Newspaper Agent application.
Run from project root: python -m pytest tests/ -v
"""

import asyncio


def test_imports():
    """Verify required packages are installed."""
    import fastapi
    import langchain
    import uvicorn
    from langchain_google_genai import ChatGoogleGenerativeAI
    assert fastapi
    assert uvicorn
    assert langchain
    assert ChatGoogleGenerativeAI


def test_env_keys_optional():
    """Env keys can be missing; stages will report unavailable."""
    from app.pipeline import NewspaperPipeline
    pipeline = NewspaperPipeline()
    assert hasattr(pipeline, "research_stage")
    assert hasattr(pipeline, "draft_stage")
    assert hasattr(pipeline, "edit_stage")
    assert hasattr(pipeline, "run_pipeline")


def test_pipeline_structure():
    """Pipeline returns expected keys; stages may be success, error, or skipped."""
    from app.pipeline import NewspaperPipeline

    pipeline = NewspaperPipeline()
    result = asyncio.run(
        pipeline.run_pipeline(topic="Test topic", max_length=500)
    )

    assert "research_stage" in result
    assert "draft_stage" in result
    assert "final_stage" in result

    valid_statuses = ("success", "error", "skipped")
    assert result["research_stage"].get("status") in valid_statuses
    assert result["draft_stage"].get("status") in valid_statuses
    assert result["final_stage"].get("status") in valid_statuses


def test_fastapi_app():
    """FastAPI app can be imported and has routes."""
    from app.main import app
    routes = [r.path for r in app.routes]
    assert "/" in routes
    assert "/health" in routes
