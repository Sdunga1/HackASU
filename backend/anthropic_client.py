"""Utility helpers to interact with the Claude Messages API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

import httpx

# Load .env file from the backend directory
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


class ClaudeClientError(RuntimeError):
    """Raised when the Claude API returns an error response."""


def get_api_key() -> str:
    """Return the Claude API key from the environment.

    Raises:
        ClaudeClientError: If the key is not configured.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ClaudeClientError(
            "Claude API key missing. Set the ANTHROPIC_API_KEY environment variable."
        )
    return api_key


async def generate_claude_response(
    prompt: str,
    *,
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> str:
    """Generate a response from Claude given a user prompt.
    
    Args:
        prompt: User's question or prompt
        model: Model name (defaults to environment variable or fallback models)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        
    Returns:
        Claude's response text
    """
    # Try models in order of preference (latest first)
    # Latest models as of 2025: Claude 3.5 Sonnet is the most recent stable release
    model_candidates = [
        model,  # User-specified model
        os.getenv("CLAUDE_MODEL"),  # Environment variable
        "claude-3-5-haiku-20241022",  # Latest Claude 3.5 Haiku (fastest)
    ]
    
    # Filter out None values and get the first available
    models_to_try = [m for m in model_candidates if m]
    if not models_to_try:
        models_to_try = ["claude-3-5-sonnet-20241022"]  # Default to latest
    
    api_key = get_api_key()
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    last_error: Optional[str] = None
    
    # System message for professional, PM-focused responses
    system_message = (
        "You are a professional project management assistant for DevAI Manager.\n\n"
        "RESPONSE FORMATTING RULES:\n"
        "- Answer questions directly and concisely - never mention 'based on dashboard information' or similar meta-commentary\n"
        "- Use context to inform answers but express insights in your own words\n"
        "- Format responses with clear sections and bullet points\n"
        "- Use **bold** for key metrics and important items\n"
        "- Structure information hierarchically:\n"
        "  * Main metrics first (bold)\n"
        "  * Key insights as bullet points\n"
        "  * Details in sub-bullets if needed\n"
        "- For greetings: Brief professional response (1-2 sentences max)\n"
        "- For data questions: Present metrics clearly, then insights\n"
        "- Avoid rhetorical questions like 'Would you like me to elaborate?' - just provide the information\n"
        "- Keep responses focused and actionable - PMs need quick, clear insights"
    )
    
    for model_name in models_to_try:
        payload: Dict[str, Any] = {
            "model": model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_message,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(CLAUDE_API_URL, headers=headers, json=payload)

        if response.status_code < 400:
            # Success - break out of the loop
            break
            
        # Extract error details
        detail: Optional[str] = None
        try:
            error_data = response.json().get("error", {})
            detail = error_data.get("message") or error_data.get("type", "Unknown error")
        except Exception:
            detail = response.text or "Unknown error"
        
        last_error = f"Model {model_name}: {detail}"
        
        # If it's a 404 (model not found), try the next model
        if response.status_code == 404:
            continue
        else:
            # For other errors, raise immediately
            raise ClaudeClientError(
                f"Claude API error ({response.status_code}): {detail or 'Unknown error'}"
            )
    else:
        # All models failed
        raise ClaudeClientError(
            f"All model attempts failed. Last error: {last_error or 'Unknown error'}"
        )

    data = response.json()
    content = data.get("content", [])
    if not content:
        raise ClaudeClientError("Claude API returned an empty response.")

    # Each content block is an object with a `text` field for text responses.
    text_blocks = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    combined = "\n".join(filter(None, text_blocks)).strip()
    if not combined:
        raise ClaudeClientError("Claude API response did not include any text blocks.")
    return combined

