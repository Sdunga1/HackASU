"""Pydantic schemas for request/response bodies."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User input question")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Claude generated answer")

