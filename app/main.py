"""
AI Newspaper Agent - FastAPI application.
Serves the web UI and article-generation API. All secrets from .env via app.config.
"""
import os
import sys

# Path bootstrap so app.config is importable (runs before app/__init__.py if needed).
_app_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
_root = os.path.dirname(_app_dir)
if _root not in sys.path:
    sys.path.insert(0, _root)

import logging
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import (
    APP_HOST,
    APP_PORT,
    DEBUG,
    DEFAULT_MAX_LENGTH,
    STATIC_DIR,
    TEMPLATES_DIR,
)
from app.pipeline import NewspaperPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Newspaper Agent",
    description="Automated journalism through sequential LLM orchestration",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

pipeline = NewspaperPipeline()


def _api_error(message: str, status_code: int = 500) -> HTTPException:
    """Log and return an HTTPException with the given message and status code."""
    logger.error("API error: %s", message)
    return HTTPException(status_code=status_code, detail=message)


class TopicRequest(BaseModel):
    topic: str
    max_length: int = 1000


class RegenerateResearchRequest(BaseModel):
    topic: str
    max_length: int = 1000


class RegenerateDraftRequest(BaseModel):
    topic: str
    max_length: int = 1000
    research_data: str


class RegenerateEditRequest(BaseModel):
    topic: str
    draft_content: str


class ArticleResponse(BaseModel):
    topic: str
    research_stage: Dict[str, Any]
    draft_stage: Dict[str, Any]
    final_stage: Dict[str, Any]
    processing_time: float


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Serve the main page with the article generation form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate", response_model=ArticleResponse)
async def generate_article(request: Request) -> ArticleResponse:
    """Run full research → draft → edit pipeline for the given topic and word limit."""
    body = await request.json()
    try:
        max_length_val = body.get("max_length", DEFAULT_MAX_LENGTH)
        max_length_val = (
            int(max_length_val) if max_length_val is not None else DEFAULT_MAX_LENGTH
        )
    except (TypeError, ValueError):
        max_length_val = DEFAULT_MAX_LENGTH
    req = TopicRequest(
        topic=body.get("topic", ""),
        max_length=max_length_val,
    )
    try:
        start = time.time()
        result = await pipeline.run_pipeline(
            topic=req.topic,
            max_length=req.max_length,
        )
        elapsed = time.time() - start
        return ArticleResponse(
            topic=req.topic,
            research_stage=result["research_stage"],
            draft_stage=result["draft_stage"],
            final_stage=result["final_stage"],
            processing_time=elapsed,
        )
    except Exception as e:
        raise _api_error(f"Error generating article: {str(e)}")


@app.post("/regenerate-research")
async def regenerate_research(req: RegenerateResearchRequest) -> Dict[str, Any]:
    """Regenerate only the research stage for the given topic."""
    try:
        start = time.time()
        result = await pipeline.research_stage(req.topic, req.max_length)
        elapsed = time.time() - start
        return {"research_stage": result, "processing_time": elapsed}
    except Exception as e:
        raise _api_error(f"Regenerate research failed: {str(e)}")


@app.post("/regenerate-draft")
async def regenerate_draft(req: RegenerateDraftRequest) -> Dict[str, Any]:
    """Regenerate only the draft stage using the provided research data."""
    try:
        start = time.time()
        result = await pipeline.draft_stage(
            req.topic, req.research_data, req.max_length
        )
        elapsed = time.time() - start
        return {"draft_stage": result, "processing_time": elapsed}
    except Exception as e:
        raise _api_error(f"Regenerate draft failed: {str(e)}")


@app.post("/regenerate-edit")
async def regenerate_edit(req: RegenerateEditRequest) -> Dict[str, Any]:
    """Regenerate only the edit stage for the given draft content."""
    try:
        start = time.time()
        max_length = max(100, len(req.draft_content.split()))
        result = await pipeline.edit_stage(
            req.topic, req.draft_content, max_length=max_length
        )
        elapsed = time.time() - start
        return {"final_stage": result, "processing_time": elapsed}
    except Exception as e:
        raise _api_error(f"Regenerate edit failed: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Return service health status for load balancers and monitoring."""
    return {"status": "healthy", "service": "AI Newspaper Agent"}


def run() -> None:
    """Start the uvicorn server for the FastAPI app."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
    )


if __name__ == "__main__":
    run()
