"""
AI Newspaper Agent - Main FastAPI Application
A browser-based application that automates the journalistic process through a structured three-stage LLM pipeline.
"""

import os
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from newspaper_pipeline import NewspaperPipeline

# Load environment variables
load_dotenv("env.env")

# Initialize FastAPI app
app = FastAPI(
    title="AI Newspaper Agent",
    description="Automated journalism through sequential LLM orchestration",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize the newspaper pipeline
pipeline = NewspaperPipeline()

class TopicRequest(BaseModel):
    topic: str
    max_length: int = 1000

class ArticleResponse(BaseModel):
    topic: str
    research_stage: Dict[str, Any]
    draft_stage: Dict[str, Any]
    final_stage: Dict[str, Any]
    processing_time: float

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-article", response_model=ArticleResponse)
async def generate_article(request: TopicRequest):
    """
    Generate a newspaper article using the three-stage LLM pipeline.
    
    Stage 1: Research using DeepSeek
    Stage 2: Draft generation using OpenAI
    Stage 3: Final editing using Google Gemini
    """
    try:
        import time
        start_time = time.time()
        
        # Run the complete pipeline
        result = await pipeline.run_pipeline(
            topic=request.topic,
            max_length=request.max_length
        )
        
        processing_time = time.time() - start_time
        
        return ArticleResponse(
            topic=request.topic,
            research_stage=result["research_stage"],
            draft_stage=result["draft_stage"],
            final_stage=result["final_stage"],
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating article: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Newspaper Agent"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
