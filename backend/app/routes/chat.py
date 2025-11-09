"""FastAPI route for the Claude-powered chatbot."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

# Add backend root to Python path to import modules at root level
backend_root = Path(__file__).parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from anthropic_client import ClaudeClientError, generate_claude_response
from schemas import ChatRequest, ChatResponse

logger = logging.getLogger("chatbot")

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
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

