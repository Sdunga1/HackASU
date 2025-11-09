"""FastAPI backend for the Claude-powered chatbot."""

from __future__ import annotations

import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from anthropic_client import ClaudeClientError, generate_claude_response
from schemas import ChatRequest, ChatResponse

logger = logging.getLogger("chatbot")

app = FastAPI(
    title="Chatbot Backend",
    description="Proxy layer that forwards user questions to Claude and returns responses.",
    version="0.1.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Simple health endpoint."""
    return {"status": "ok"}


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

