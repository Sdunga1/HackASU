from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import issues, stats, ai, dashboard, chat
from app.config import settings

from __future__ import annotations

import logging
from typing import Dict

from anthropic_client import ClaudeClientError, generate_claude_response
from schemas import ChatRequest, ChatResponse


logger = logging.getLogger("chatbot")

app = FastAPI(
    title="DevAI Manager API",
    description="AI-powered project management API for GitHub and Jira",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(issues.router, prefix="/api", tags=["issues"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
async def root():
    return {
        "message": "DevAI Manager API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Receive a user question, forward to Claude, and return the answer."""
    try:
        answer = await generate_claude_response(request.question)
    except ClaudeClientError as exc:
        logger.exception("Claude client error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error while contacting Claude.")
        raise HTTPException(status_code=500, detail="Unexpected error") from exc

    return ChatResponse(answer=answer)

