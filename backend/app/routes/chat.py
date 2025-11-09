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
    """Receive a user question with optional page context, forward to Claude, and return the answer."""
    try:
        # Determine if context is relevant to this question
        question_lower = request.question.lower().strip()
        question_words = question_lower.split()
        
        # Simple greetings or very short questions don't need context
        simple_greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        is_simple_greeting = (
            any(question_lower.startswith(greeting) for greeting in simple_greetings) and 
            len(question_words) <= 3
        ) or len(question_words) <= 2
        
        # Check if question explicitly asks about the page/dashboard/project (context-relevant)
        # Only include context if question is substantial and mentions project-related terms
        context_keywords = ['dashboard', 'page', 'project', 'issue', 'sprint', 'status', 'metric', 
                           'progress', 'show', 'tell', 'explain', 'analyze', 'summary', 'overview', 
                           'current', 'how many', 'what are', 'which', 'list']
        needs_context = (
            not is_simple_greeting and 
            len(question_words) > 2 and
            any(keyword in question_lower for keyword in context_keywords)
        )
        
        # Build the prompt
        if needs_context and (request.pageContext or request.contextHistory):
            # Include context for relevant questions - structure it so Claude answers using context, not repeats it
            prompt_parts = [
                f"Question: {request.question}\n\n",
                "Answer using the following project data. Present the answer in a clear, structured format with key metrics first, then insights. Do not mention 'based on' or 'dashboard information' - just provide the answer directly:\n\n"
            ]
            
            if request.pageContext:
                # Limit context size to avoid overwhelming the prompt
                context = request.pageContext
                # If context is very long, summarize key parts
                if len(context) > 2000:
                    prompt_parts.append(context[:2000] + "... [context truncated]")
                else:
                    prompt_parts.append(context)
            
            if request.contextHistory:
                if request.pageContext:
                    prompt_parts.append("\n")
                prompt_parts.append(request.contextHistory)
            
            full_prompt = "\n".join(prompt_parts)
        else:
            # Simple questions without context - just answer normally
            full_prompt = request.question
        
        answer = await generate_claude_response(full_prompt)
    except ClaudeClientError as exc:
        logger.exception("Claude client error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error while contacting Claude.")
        raise HTTPException(status_code=500, detail="Unexpected error") from exc

    return ChatResponse(answer=answer)

