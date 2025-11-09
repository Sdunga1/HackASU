"""Pydantic schemas for request/response bodies."""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User input question")
    pageContext: Optional[str] = Field(None, description="Current page context for AI")
    contextHistory: Optional[str] = Field(None, description="Context history from previous pages")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Claude generated answer")

