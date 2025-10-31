from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.core.config import settings

load_dotenv()

app = FastAPI(
    title="Self-Evolving Agent Platform",
    description="MVP for a self-evolving AI agent platform with dual-agent architecture",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])


@app.get("/")
async def root():
    """Root endpoint with basic platform information."""
    return {
        "message": "Self-Evolving Agent Platform MVP",
        "version": "0.1.0",
        "status": "active",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-10-31T15:23:00Z"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
